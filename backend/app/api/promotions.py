"""
Promotions API endpoints
"""

from fastapi import APIRouter, Depends
from app.models.user import User
from app.schemas.service import PromotionResponse
from app.dependencies import get_current_active_user

router = APIRouter()


@router.get("/", response_model=list[PromotionResponse])
async def get_promotions(
    current_user: User = Depends(get_current_active_user)
):
    """
    Lấy danh sách chương trình khuyến mãi
    """
    promotions = [
        PromotionResponse(
            id="first_order",
            name="Giảm giá đơn hàng đầu tiên",
            description="Giảm 10% cho đơn hàng đầu tiên của bạn",
            discount_percentage=10,
            min_amount=10.0,
            max_discount=50.0,
            is_active=True
        ),
        PromotionResponse(
            id="bulk_discount",
            name="Giảm giá số lượng lớn",
            description="Giảm 15% cho đơn hàng từ 10,000 đơn vị trở lên",
            discount_percentage=15,
            min_amount=100.0,
            max_discount=200.0,
            is_active=True
        ),
        PromotionResponse(
            id="valentine_bonus",
            name="Bonus Valentine 14/02",
            description="Tặng thêm 20% số dư khi nạp tiền trong ngày Valentine",
            discount_percentage=20,
            min_amount=50.0,
            max_discount=100.0,
            is_active=False  # Chỉ active vào ngày Valentine
        ),
        PromotionResponse(
            id="new_year_bonus",
            name="Bonus Tết Nguyên Đán",
            description="Tặng thêm 30% số dư khi nạp tiền trong dịp Tết",
            discount_percentage=30,
            min_amount=100.0,
            max_discount=500.0,
            is_active=False  # Chỉ active trong dịp Tết
        )
    ]
    
    # Filter chỉ active promotions
    active_promotions = [p for p in promotions if p.is_active]
    
    return active_promotions
