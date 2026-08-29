"""Views for the core app.

Includes the dashboard home page (aggregate summary of risks/tasks) plus
full CRUD for the three organizational master-data models. Create/Update
require manager-or-above; Delete requires admin (see apps.common.mixins).
"""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, TemplateView

from apps.common.mixins import AdminRequiredMixin, ManagerRequiredMixin
from apps.core.forms import BusinessUnitForm, CommitteeForm, FunctionForm
from apps.core.models import BusinessUnit, Committee, Function


class DashboardView(LoginRequiredMixin, TemplateView):
    """The team's landing page: a quick-glance summary so anyone can see
    what needs attention today without navigating anywhere."""

    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        from apps.grc.models import Risk, Control
        from apps.tasks.models import Task

        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.localdate()

        context["open_risk_count"] = Risk.objects.filter(status=Risk.Status.OPEN).count()
        context["high_severity_open_risks"] = (
            Risk.objects.filter(status=Risk.Status.OPEN, severity=Risk.Severity.HIGH)
            .select_related("business_unit").order_by("-created_at")[:5]
        )
        context["control_count"] = Control.objects.count()
        context["ineffective_control_count"] = Control.objects.filter(
            effectiveness=Control.Effectiveness.INEFFECTIVE
        ).count()

        my_tasks = Task.objects.filter(owner=user).exclude(status=Task.Status.DONE)
        context["my_open_task_count"] = my_tasks.count()
        context["my_overdue_task_count"] = my_tasks.filter(due_date__lt=today).count()
        context["my_upcoming_tasks"] = my_tasks.order_by("due_date")[:5]

        context["business_unit_count"] = BusinessUnit.objects.count()
        context["committee_count"] = Committee.objects.count()
        return context


# ---------------------------------------------------------------------------
# BusinessUnit CRUD
# ---------------------------------------------------------------------------
class BusinessUnitListView(LoginRequiredMixin, ListView):
    model = BusinessUnit
    context_object_name = "business_units"
    template_name = "core/business_unit_list.html"
    paginate_by = 20

    def get_queryset(self):
        qs = BusinessUnit.objects.select_related("head").annotate(
            function_count=Count("functions", distinct=True)
        )
        query = self.request.GET.get("q")
        if query:
            qs = qs.filter(Q(name__icontains=query) | Q(code__icontains=query))
        return qs


class BusinessUnitDetailView(LoginRequiredMixin, DetailView):
    model = BusinessUnit
    context_object_name = "business_unit"
    template_name = "core/business_unit_detail.html"

    def get_queryset(self):
        return BusinessUnit.objects.select_related("head").prefetch_related("functions", "committees")


class BusinessUnitCreateView(ManagerRequiredMixin, CreateView):
    model = BusinessUnit
    form_class = BusinessUnitForm
    template_name = "core/business_unit_form.html"

    def form_valid(self, form):
        messages.success(self.request, f"Business unit '{form.instance.name}' created.")
        return super().form_valid(form)


class BusinessUnitUpdateView(ManagerRequiredMixin, UpdateView):
    model = BusinessUnit
    form_class = BusinessUnitForm
    template_name = "core/business_unit_form.html"

    def form_valid(self, form):
        messages.success(self.request, f"Business unit '{form.instance.name}' updated.")
        return super().form_valid(form)


class BusinessUnitDeleteView(AdminRequiredMixin, DeleteView):
    model = BusinessUnit
    template_name = "partials/confirm_delete.html"
    success_url = reverse_lazy("core:business_unit_list")

    def form_valid(self, form):
        messages.success(self.request, "Business unit deleted.")
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# Function CRUD
# ---------------------------------------------------------------------------
class FunctionListView(LoginRequiredMixin, ListView):
    model = Function
    context_object_name = "functions"
    template_name = "core/function_list.html"
    paginate_by = 20

    def get_queryset(self):
        return Function.objects.select_related("business_unit")


class FunctionDetailView(LoginRequiredMixin, DetailView):
    model = Function
    context_object_name = "function"
    template_name = "core/function_detail.html"

    def get_queryset(self):
        return Function.objects.select_related("business_unit")


class FunctionCreateView(ManagerRequiredMixin, CreateView):
    model = Function
    form_class = FunctionForm
    template_name = "core/function_form.html"

    def form_valid(self, form):
        messages.success(self.request, f"Function '{form.instance.name}' created.")
        return super().form_valid(form)


class FunctionUpdateView(ManagerRequiredMixin, UpdateView):
    model = Function
    form_class = FunctionForm
    template_name = "core/function_form.html"

    def form_valid(self, form):
        messages.success(self.request, f"Function '{form.instance.name}' updated.")
        return super().form_valid(form)


class FunctionDeleteView(AdminRequiredMixin, DeleteView):
    model = Function
    template_name = "partials/confirm_delete.html"
    success_url = reverse_lazy("core:function_list")

    def form_valid(self, form):
        messages.success(self.request, "Function deleted.")
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# Committee CRUD
# ---------------------------------------------------------------------------
class CommitteeListView(LoginRequiredMixin, ListView):
    model = Committee
    context_object_name = "committees"
    template_name = "core/committee_list.html"
    paginate_by = 20

    def get_queryset(self):
        return Committee.objects.select_related("business_unit", "chair").prefetch_related("members")


class CommitteeDetailView(LoginRequiredMixin, DetailView):
    model = Committee
    context_object_name = "committee"
    template_name = "core/committee_detail.html"

    def get_queryset(self):
        return Committee.objects.select_related("business_unit", "chair").prefetch_related("members")


class CommitteeCreateView(ManagerRequiredMixin, CreateView):
    model = Committee
    form_class = CommitteeForm
    template_name = "core/committee_form.html"

    def form_valid(self, form):
        messages.success(self.request, f"Committee '{form.instance.name}' created.")
        return super().form_valid(form)


class CommitteeUpdateView(ManagerRequiredMixin, UpdateView):
    model = Committee
    form_class = CommitteeForm
    template_name = "core/committee_form.html"

    def form_valid(self, form):
        messages.success(self.request, f"Committee '{form.instance.name}' updated.")
        return super().form_valid(form)


class CommitteeDeleteView(AdminRequiredMixin, DeleteView):
    model = Committee
    template_name = "partials/confirm_delete.html"
    success_url = reverse_lazy("core:committee_list")

    def form_valid(self, form):
        messages.success(self.request, "Committee deleted.")
        return super().form_valid(form)
