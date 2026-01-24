from typing import Tuple

from django.utils import timezone

from orders.models import Order


class OrderCancellationService:
    @staticmethod
    def request_cancellation(order: Order, reason: str) -> Tuple[bool, str]:
        if order.status == Order.Status.CANCELLED:
            return False, "이미 취소된 주문입니다."
        
        if order.cancellation_request_status != Order.CancellationRequestStatus.NONE:
            return False, "이미 취소 요청이 처리되었거나 진행 중입니다."
        
        order.cancellation_request_status = Order.CancellationRequestStatus.PENDING
        order.cancellation_reason = reason
        order.cancellation_requested_at = timezone.now()
        order.save(update_fields=["cancellation_request_status", "cancellation_reason", "cancellation_requested_at"])
        
        return True, "취소 요청이 접수되었습니다. 관리자 검토 후 처리됩니다."

    @staticmethod
    def approve_cancellation(order: Order, admin_note: str | None = None) -> Tuple[bool, str]:
        if order.cancellation_request_status != Order.CancellationRequestStatus.PENDING:
            return False, "처리할 수 없는 취소 요청입니다."
        
        order.cancellation_request_status = Order.CancellationRequestStatus.APPROVED
        order.status = Order.Status.CANCELLED
        order.cancellation_processed_at = timezone.now()
        if admin_note:
            order.cancellation_admin_note = admin_note
        order.save(update_fields=["cancellation_request_status", "status", "cancellation_processed_at", "cancellation_admin_note"])
        
        return True, f"주문 {order.order_id}의 취소 요청이 승인되었습니다."

    @staticmethod
    def reject_cancellation(order: Order, admin_note: str) -> Tuple[bool, str]:
        if order.cancellation_request_status != Order.CancellationRequestStatus.PENDING:
            return False, "처리할 수 없는 취소 요청입니다."
        
        if not admin_note or not admin_note.strip():
            return False, "거부 사유를 입력해주세요."
        
        order.cancellation_request_status = Order.CancellationRequestStatus.REJECTED
        order.cancellation_processed_at = timezone.now()
        order.cancellation_admin_note = admin_note.strip()
        order.save(update_fields=["cancellation_request_status", "cancellation_processed_at", "cancellation_admin_note"])
        
        return True, f"주문 {order.order_id}의 취소 요청이 거부되었습니다."
