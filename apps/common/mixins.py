"""Reusable class-based-view mixins shared by every CRUD app.

Keeping permission logic here (instead of copy-pasting `if` checks into
every view) means the three-tier role model (admin / manager / member)
is enforced consistently across BusinessUnit, Committee, Risk, Control,
and Task views.
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class ManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restricts a view to managers and admins — used for create/update
    views on shared master data (BusinessUnit, Function, Committee,
    Risk, Control) that regular members can view but not edit."""

    def test_func(self) -> bool:
        return self.request.user.is_manager_or_above

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("You need manager or admin access for this action.")
        return super().handle_no_permission()


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restricts a view to admins only — used for destructive actions
    (deleting a BusinessUnit, Committee, etc.) where an accidental click
    by a manager could break history for lots of dependent records."""

    def test_func(self) -> bool:
        return self.request.user.is_admin_role

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("You need admin access for this action.")
        return super().handle_no_permission()


class OwnerOrManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """For Task objects: the assigned owner can always edit their own
    task; managers/admins can edit anyone's. Everyone else is blocked at
    the object level even if they guess the URL."""

    def test_func(self) -> bool:
        obj = self.get_object()
        user = self.request.user
        return user.is_manager_or_above or getattr(obj, "owner_id", None) == user.id
