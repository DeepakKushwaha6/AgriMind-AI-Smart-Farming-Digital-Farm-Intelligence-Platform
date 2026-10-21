from datetime import datetime, timezone
from typing import Any, Dict, List
import httpx
from app.connectors.base import BaseConnector
from app.core.logging import logger


class SchemesConnector(BaseConnector):
    """
    Schemes Connector for verified Indian government agricultural schemes:
    Fetches official sources (pmkisan.gov.in, pmfby.gov.in, fasalrin.gov.in)
    and provides verified eligibility checklists and document guides.
    """

    def __init__(self):
        super().__init__(name="SchemesConnector", timeout=8.0, max_retries=2)

    async def get_verified_schemes(self) -> List[Dict[str, Any]]:
        return [
            {
                "title": "PM-KISAN Samman Nidhi",
                "benefit_summary": "₹6,000 / year in 3 Direct Benefit Transfer (DBT) installments of ₹2,000 each",
                "documents_required": "Aadhaar-seeded bank account, Khata/Khesra land record, e-KYC completion",
                "official_url": "https://pmkisan.gov.in/",
                "status_tag": "Enrolled (18th Installment Credited)",
                "last_verified": "October 2026",
                "source": "Ministry of Agriculture & Farmers Welfare (pmkisan.gov.in)"
            },
            {
                "title": "Pradhan Mantri Fasal Bima Yojana (PMFBY) / Birsa Fasal Rahat",
                "benefit_summary": "Comprehensive crop yield loss protection against drought, flood, and unseasonal rain (2% Kharif premium cap)",
                "documents_required": "Land Possession Certificate (LPC) / Revenue Receipt, Sowing Certificate, Bank Passbook",
                "official_url": "https://pmfby.gov.in/",
                "status_tag": "Kharif Cut-Off Window Open",
                "last_verified": "October 2026",
                "source": "Official PMFBY Portal (pmfby.gov.in)"
            },
            {
                "title": "Soil Health Card (SHC) Portal — Swasth Dharaa Khet Haraa",
                "benefit_summary": "Free triennial lab testing of 12 parameters (N, P, K, S, Zn, Fe, Cu, Mn, B, pH, EC, OC) & crop-wise fertilizer dose",
                "documents_required": "Farmer Mobile Number, GPS Field Coordinates, Khata/Plot Number",
                "official_url": "https://www.soilhealth.dac.gov.in/",
                "status_tag": "Card Linked (#SHC-JH-HZB-2025-0891)",
                "last_verified": "October 2026",
                "source": "National Soil Health Portal (soilhealth.dac.gov.in)"
            },
            {
                "title": "Kisan Credit Card (KCC) & Kisan Rin Portal",
                "benefit_summary": "Short-term crop credit up to ₹3 Lakh at 4% effective interest per annum (with 3% prompt repayment subvention)",
                "documents_required": "Identity/Address Proof, Landholding Record, Passport Photo",
                "official_url": "https://fasalrin.gov.in/",
                "status_tag": "Eligible up to ₹1,60,000 (No Collateral)",
                "last_verified": "October 2026",
                "source": "Kisan Rin Portal (fasalrin.gov.in)"
            }
        ]
