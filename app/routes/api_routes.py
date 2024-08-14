# api_routes.py
from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.Token import Token
import requests
from datetime import datetime
from app.models.Item import Item
from app.schemas.item_schema import BaseItem
import json

router = APIRouter()


@router.get("/numbers/list")
async def get_numbers(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = auth_header.split(" ")[1]
    token_db = db.query(Token).filter(Token.access_token == token).first()
    if not token_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found")

    # Call the external API to retrieve numbers
    api_key = 'a4431b2d62ae9ea8f59b4f7199e9ecbe'
    url = "https://api.vocode.dev/v1/numbers/list"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.request("GET", url, headers=headers)

    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content}")

    if response.status_code == 200:
        vocode_numbers = response.json()["items"]
        item_schemas = []

        try:
            for vocode_number in vocode_numbers:
                number = vocode_number["number"]
                existing_item = db.query(Item).filter(Item.number == number).first()
                if existing_item:
                    item_schema = BaseItem(
                        id=existing_item.id,
                        vocode_ai_id=existing_item.vocode_ai_id,
                        client_id=existing_item.client_id,
                        user_id=existing_item.user_id,
                        active=existing_item.active,
                        label=existing_item.label,
                        inbound_agent=existing_item.inbound_agent,
                        outbound_only=existing_item.outbound_only,
                        number=existing_item.number,
                        telephony_provider=existing_item.telephony_provider,
                        telephony_account_connection=existing_item.telephony_account_connection,
                        created_at=existing_item.created_at,
                        updated_at=existing_item.updated_at
                    )
                    item_schemas.append(item_schema)
                else:
                    # Create a new item in the database
                    item = Item(
                        vocode_ai_id=vocode_number["id"],
                        client_id=vocode_number["user_id"],
                        user_id=token_db.user_id,
                        active=vocode_number["active"],
                        label=vocode_number["label"],
                        inbound_agent=vocode_number["inbound_agent"],
                        outbound_only=vocode_number["outbound_only"],
                        example_context=vocode_number["example_context"],
                        number=vocode_number["number"],
                        telephony_provider=vocode_number["telephony_provider"],
                        telephony_account_connection=vocode_number["telephony_account_connection"],
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.add(item)
                    db.commit()
                    item_schema = BaseItem(
                        id=item.id,
                        vocode_ai_id=item.vocode_ai_id,
                        client_id=item.client_id,
                        user_id=item.user_id,
                        active=item.active,
                        label=item.label,
                        inbound_agent=item.inbound_agent,
                        outbound_only=item.outbound_only,
                        number=item.number,
                        telephony_provider=item.telephony_provider,
                        telephony_account_connection=item.telephony_account_connection,
                        created_at=item.created_at,
                        updated_at=item.updated_at
                    )
                    item_schemas.append(item_schema)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Error creating item: {str(e)}")

        return {"numbers": item_schemas}
    else:
        raise HTTPException(status_code=response.status_code, detail=f"Error retrieving numbers: {response.content}")