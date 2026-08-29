"""Views for the grc app: Risk register and Control library CRUD.

Follows the same permission shape as apps.core: everyone can view,
managers/admins can create/edit, admins can delete (see
apps.common.mixins). Risk notification-on-create is handled by a signal
(apps/grc/signals.py) rather than inline here, as a second example of
the notification hook pattern alongside the explicit-in-view approach
used in apps.tasks.
"""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.common.mixins import AdminRequiredMixin, ManagerRequiredMixin
from apps.grc.forms import ControlForm, RiskForm
from apps.grc.models import Control, Risk


# ---------------------------------------------------------------------------
# Risk CRUD
# ---------------------------------------------------------------------------
class RiskListView(LoginRequiredMixin, ListView):
    model = Risk
    context_object_name = "risks"
    template_name = "grc/risk_list.html"
    paginate_by = 25

    def get_queryset(self):
        qs = Risk.objects.select_related("business_unit", "function", "owner")

        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)

        severity = self.request.GET.get("severity")
        if severity:
            qs = qs.filter(severity=severity)

        query = self.request.GET.get("q")
        if query:
            qs = qs.filter(Q(title__icontains=query) | Q(description__icontains=query))

        return qs.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = Risk.Status.choices
        context["severity_choices"] = Risk.Severity.choices
        context["current_status"] = self.request.GET.get("status", "")
        context["current_severity"] = self.request.GET.get("severity", "")
        context["query"] = self.request.GET.get("q", "")
        return context


class RiskDetailView(LoginRequiredMixin, DetailView):
    model = Risk
    context_object_name = "risk"
    template_name = "grc/risk_detail.html"

    def get_queryset(self):
        return Risk.objects.select_related("business_unit", "function", "owner").prefetch_related("controls")


class RiskCreateView(ManagerRequiredMixin, CreateView):
    model = Risk
    form_class = RiskForm
    template_name = "grc/risk_form.html"

    def form_valid(self, form):
        messages.success(self.request, f"Risk '{form.instance.title}' created.")
        return super().form_valid(form)


class RiskUpdateView(ManagerRequiredMixin, UpdateView):
    model = Risk
    form_class = RiskForm
    template_name = "grc/risk_form.html"

    def form_valid(self, form):
        messages.success(self.request, f"Risk '{form.instance.title}' updated.")
        return super().form_valid(form)


class RiskDeleteView(AdminRequiredMixin, DeleteView):
    model = Risk
    template_name = "partials/confirm_delete.html"
    success_url = reverse_lazy("grc:risk_list")

    def form_valid(self, form):
        messages.success(self.request, "Risk deleted.")
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# Control CRUD
# ---------------------------------------------------------------------------
class ControlListView(LoginRequiredMixin, ListView):
    model = Control
    context_object_name = "controls"
    template_name = "grc/control_list.html"
    paginate_by = 25

    def get_queryset(self):
        return Control.objects.select_related("risk", "owner").order_by("-created_at")


class ControlDetailView(LoginRequiredMixin, DetailView):
    model = Control
    context_object_name = "control"
    template_name = "grc/control_detail.html"

    def get_queryset(self):
        return Control.objects.select_related("risk", "owner")


class ControlCreateView(ManagerRequiredMixin, CreateView):
    model = Control
    form_class = ControlForm
    template_name = "grc/control_form.html"

    def form_valid(self, form):
        messages.success(self.request, f"Control '{form.instance.title}' created.")
        return super().form_valid(form)


class ControlUpdateView(ManagerRequiredMixin, UpdateView):
    model = Control
    form_class = ControlForm
    template_name = "grc/control_form.html"

    def form_valid(self, form):
        messages.success(self.request, f"Control '{form.instance.title}' updated.")
        return super().form_valid(form)


class ControlDeleteView(AdminRequiredMixin, DeleteView):
    model = Control
    template_name = "partials/confirm_delete.html"
    success_url = reverse_lazy("grc:control_list")

    def form_valid(self, form):
        messages.success(self.request, "Control deleted.")
        return super().form_valid(form)
