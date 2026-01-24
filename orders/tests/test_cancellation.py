import pytest
from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils import timezone

from config.utils.setup_test_method import TestSetupMixin
from orders.models import Order
from orders.services.order_cancellation_services import OrderCancellationService


@pytest.mark.django_db
class TestOrderCancellationService(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()
        self.setup_test_order_data()

    def test_request_cancellation_success(self) -> None:
        reason = Order.CancellationReason.SIZE_MISMATCH
        
        success, message = OrderCancellationService.request_cancellation(self.order, reason)
        
        assert success is True
        assert "접수되었습니다" in message
        self.order.refresh_from_db()
        assert self.order.cancellation_request_status == "PENDING"
        assert self.order.cancellation_reason == reason
        assert self.order.cancellation_requested_at is not None

    def test_request_cancellation_already_cancelled(self) -> None:
        self.order.status = "CANCELLED"
        self.order.save()
        reason = Order.CancellationReason.SIZE_MISMATCH
        
        success, message = OrderCancellationService.request_cancellation(self.order, reason)
        
        assert success is False
        assert "이미 취소된 주문입니다" in message

    def test_request_cancellation_already_pending(self) -> None:
        self.order.cancellation_request_status = "PENDING"
        self.order.save()
        reason = Order.CancellationReason.SIZE_MISMATCH
        
        success, message = OrderCancellationService.request_cancellation(self.order, reason)
        
        assert success is False
        assert "이미 취소 요청이 처리되었거나 진행 중입니다" in message

    def test_request_cancellation_empty_reason(self) -> None:
        success, message = OrderCancellationService.request_cancellation(self.order, "")
        
        assert success is False
        assert "취소 사유를 선택해주세요" in message

    def test_request_cancellation_invalid_reason(self) -> None:
        success, message = OrderCancellationService.request_cancellation(self.order, "INVALID_REASON")
        
        assert success is False
        assert "유효하지 않은 취소 사유입니다" in message

    def test_approve_cancellation_success(self) -> None:
        self.order.cancellation_request_status = "PENDING"
        self.order.save()
        admin_note = "승인 메모"
        
        success, message = OrderCancellationService.approve_cancellation(self.order, admin_note)
        
        assert success is True
        assert "승인되었습니다" in message
        self.order.refresh_from_db()
        assert self.order.cancellation_request_status == "APPROVED"
        assert self.order.status == "CANCELLED"
        assert self.order.cancellation_admin_note == admin_note
        assert self.order.cancellation_processed_at is not None

    def test_approve_cancellation_without_admin_note(self) -> None:
        self.order.cancellation_request_status = "PENDING"
        self.order.save()
        
        success, message = OrderCancellationService.approve_cancellation(self.order, None)
        
        assert success is True
        self.order.refresh_from_db()
        assert self.order.cancellation_request_status == "APPROVED"
        assert self.order.status == "CANCELLED"

    def test_approve_cancellation_not_pending(self) -> None:
        self.order.cancellation_request_status = "APPROVED"
        self.order.save()
        
        success, message = OrderCancellationService.approve_cancellation(self.order, None)
        
        assert success is False
        assert "처리할 수 없는 취소 요청입니다" in message

    def test_reject_cancellation_success(self) -> None:
        self.order.cancellation_request_status = "PENDING"
        self.order.save()
        admin_note = "거부 사유"
        
        success, message = OrderCancellationService.reject_cancellation(self.order, admin_note)
        
        assert success is True
        assert "거부되었습니다" in message
        self.order.refresh_from_db()
        assert self.order.cancellation_request_status == "REJECTED"
        assert self.order.cancellation_admin_note == admin_note
        assert self.order.cancellation_processed_at is not None

    def test_reject_cancellation_empty_admin_note(self) -> None:
        self.order.cancellation_request_status = "PENDING"
        self.order.save()
        
        success, message = OrderCancellationService.reject_cancellation(self.order, "")
        
        assert success is False
        assert "거부 사유를 입력해주세요" in message

    def test_reject_cancellation_whitespace_admin_note(self) -> None:
        self.order.cancellation_request_status = "PENDING"
        self.order.save()
        
        success, message = OrderCancellationService.reject_cancellation(self.order, "   ")
        
        assert success is False
        assert "거부 사유를 입력해주세요" in message

    def test_reject_cancellation_not_pending(self) -> None:
        self.order.cancellation_request_status = "APPROVED"
        self.order.save()
        
        success, message = OrderCancellationService.reject_cancellation(self.order, "거부 사유")
        
        assert success is False
        assert "처리할 수 없는 취소 요청입니다" in message


@pytest.mark.django_db
class TestOrderCancellationRequestView(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()
        self.setup_test_order_data()

    def test_get_redirects_to_status(self) -> None:
        self.client.force_login(self.customer_user)
        url = reverse("orders:cancel-request", kwargs={"order_id": self.order.id})
        
        response = self.client.get(url)
        
        assert response.status_code == 302
        assert response["Location"] == reverse("orders:status")

    def test_post_success(self) -> None:
        self.order.user = self.customer_user
        self.order.save()
        self.client.force_login(self.customer_user)
        url = reverse("orders:cancel-request", kwargs={"order_id": self.order.id})
        
        response = self.client.post(url, {
            "reason": Order.CancellationReason.SIZE_MISMATCH
        }, follow=True)
        
        assert response.status_code == 200
        messages_list = list(get_messages(response.wsgi_request))
        assert any("접수되었습니다" in str(msg) for msg in messages_list)
        self.order.refresh_from_db()
        assert self.order.cancellation_request_status == "PENDING"

    def test_post_already_cancelled(self) -> None:
        self.order.user = self.customer_user
        self.order.status = "CANCELLED"
        self.order.save()
        self.client.force_login(self.customer_user)
        url = reverse("orders:cancel-request", kwargs={"order_id": self.order.id})
        
        response = self.client.post(url, {
            "reason": Order.CancellationReason.SIZE_MISMATCH
        }, follow=True)
        
        assert response.status_code == 200
        messages_list = list(get_messages(response.wsgi_request))
        assert any("이미 취소된 주문입니다" in str(msg) for msg in messages_list)

    def test_post_invalid_reason(self) -> None:
        self.order.user = self.customer_user
        self.order.save()
        self.client.force_login(self.customer_user)
        url = reverse("orders:cancel-request", kwargs={"order_id": self.order.id})
        
        response = self.client.post(url, {
            "reason": ""
        }, follow=True)
        
        assert response.status_code == 200
        messages_list = list(get_messages(response.wsgi_request))
        assert any("취소 사유를 선택해주세요" in str(msg) for msg in messages_list)

    def test_post_unauthorized_user(self) -> None:
        self.client.force_login(self.customer_user)
        url = reverse("orders:cancel-request", kwargs={"order_id": self.order.id})
        
        response = self.client.post(url, {
            "reason": Order.CancellationReason.SIZE_MISMATCH
        })
        
        assert response.status_code == 404


@pytest.mark.django_db
class TestAdminCancellationListView(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()
        self.setup_test_order_data()
        self.order.cancellation_request_status = "PENDING"
        self.order.cancellation_reason = Order.CancellationReason.SIZE_MISMATCH
        self.order.cancellation_requested_at = timezone.now()
        self.order.save()

    def test_admin_cancellation_list(self) -> None:
        self.client.force_login(self.admin_user)
        url = reverse("orders:admin-cancellation-list")
        
        response = self.client.get(url)
        
        assert response.status_code == 200
        assert "orders/admin/cancellation_list.html" in [t.name for t in response.templates]
        assert response.context["q"] == ""
        assert response.context["status"] == ""
        orders = list(response.context["orders"])
        assert len(orders) > 0

    def test_admin_cancellation_list_with_search(self) -> None:
        self.client.force_login(self.admin_user)
        url = reverse("orders:admin-cancellation-list")
        
        response = self.client.get(url, {"q": "123456"})
        
        assert response.status_code == 200
        assert response.context["q"] == "123456"
        orders = list(response.context["orders"])
        assert len(orders) > 0
        assert all("123456" in o.order_id for o in orders)

    def test_admin_cancellation_list_with_status_filter(self) -> None:
        self.client.force_login(self.admin_user)
        url = reverse("orders:admin-cancellation-list")
        
        response = self.client.get(url, {"status": "PENDING"})
        
        assert response.status_code == 200
        assert response.context["status"] == "PENDING"
        orders = list(response.context["orders"])
        assert len(orders) > 0
        assert all(o.cancellation_request_status == "PENDING" for o in orders)


@pytest.mark.django_db
class TestAdminCancellationProcessView(TestSetupMixin):
    def setup_method(self) -> None:
        self.setup_test_user_data()
        self.setup_test_products_data()
        self.setup_test_order_data()
        self.order.cancellation_request_status = "PENDING"
        self.order.save()

    def test_approve_cancellation(self) -> None:
        self.client.force_login(self.admin_user)
        url = reverse("orders:admin-cancellation-process", kwargs={"order_id": self.order.id})
        
        response = self.client.post(url, {
            "action": "approve",
            "admin_note": "승인 메모"
        }, follow=True)
        
        assert response.status_code == 200
        messages_list = list(get_messages(response.wsgi_request))
        assert any("승인되었습니다" in str(msg) for msg in messages_list)
        self.order.refresh_from_db()
        assert self.order.cancellation_request_status == "APPROVED"
        assert self.order.status == "CANCELLED"

    def test_reject_cancellation(self) -> None:
        self.client.force_login(self.admin_user)
        url = reverse("orders:admin-cancellation-process", kwargs={"order_id": self.order.id})
        
        response = self.client.post(url, {
            "action": "reject",
            "admin_note": "거부 사유"
        }, follow=True)
        
        assert response.status_code == 200
        messages_list = list(get_messages(response.wsgi_request))
        assert any("거부되었습니다" in str(msg) for msg in messages_list)
        self.order.refresh_from_db()
        assert self.order.cancellation_request_status == "REJECTED"

    def test_reject_cancellation_without_admin_note(self) -> None:
        self.client.force_login(self.admin_user)
        url = reverse("orders:admin-cancellation-process", kwargs={"order_id": self.order.id})
        
        response = self.client.post(url, {
            "action": "reject",
            "admin_note": ""
        }, follow=True)
        
        assert response.status_code == 200
        messages_list = list(get_messages(response.wsgi_request))
        assert any("거부 사유를 입력해주세요" in str(msg) for msg in messages_list)

    def test_invalid_action(self) -> None:
        self.client.force_login(self.admin_user)
        url = reverse("orders:admin-cancellation-process", kwargs={"order_id": self.order.id})
        
        response = self.client.post(url, {
            "action": "invalid_action",
            "admin_note": ""
        }, follow=True)
        
        assert response.status_code == 200
        messages_list = list(get_messages(response.wsgi_request))
        assert any("잘못된 요청입니다" in str(msg) for msg in messages_list)
