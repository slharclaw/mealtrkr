import os
from dotenv import load_dotenv
from typing import Dict, Optional, List
from datetime import datetime
import httpx
from schemas import Product, Location, SearchProductsResponse, CartTotal

load_dotenv()


class KrogerClient:
    """Wrapper around kroger-api forShopping API integration."""

    def __init__(self):
        self.client_id = os.getenv("KROGER_CLIENT_ID")
        self.client_secret = os.getenv("KROGER_CLIENT_SECRET")
        self.base_url = "https://api.kroger.com/v1"

        # We'll implement the OAuth flow manually since we need custom token management
        self.access_token = None
        self.token_expiry = None

    async def get_token(self) -> str:
        """Get or refresh OAuth token."""
        # For now, return a placeholder
        # In production, implement proper OAuth2 client credentials flow
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.access_token

        # Client credentials grant flow
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/oauth2/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "scope": "product.compact cart.basic:write"
                }
            )
            response.raise_for_status()
            data = response.json()
            self.access_token = data["access_token"]
            self.token_expiry = datetime.now() + datetime.timedelta(seconds=data["expires_in"])
            return self.access_token

    async def search_locations(self, zip_code: str, radius: int = 10, limit: int = 5) -> Dict:
        """Search for store locations by zip code."""
        token = await self.get_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/locations",
                headers={"Authorization": f"Bearer {token}"},
                params={
                    "filter.zipCode.near": zip_code,
                    "filter.radius": radius,
                    "filter.limit": limit
                }
            )
            response.raise_for_status()
            return response.json()

    async def search_products(
        self,
        term: str,
        location_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> SearchProductsResponse:
        """Search for products."""
        token = await self.get_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/products",
                headers={"Authorization": f"Bearer {token}"},
                params={
                    "filter.term": term,
                    "filter.locationId": location_id,
                    "filter.limit": limit,
                    "filter.offset": offset
                }
            )
            response.raise_for_status()
            return SearchProductsResponse(**response.json())

    async def get_product_details(self, product_id: str) -> Optional[Product]:
        """Get detailed product information."""
        token = await self.get_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/products/{product_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                data = response.json()
                return Product(**data.get("data", {}))
            return None

    async def get_product_images(self, product_id: str) -> Optional[str]:
        """Get product image URL."""
        token = await self.get_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/products/{product_id}/images",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("items", [{}])[0].get("url", None)
            return None
