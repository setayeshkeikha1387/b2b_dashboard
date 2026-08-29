"""Views for the tasks app.

Anyone logged in can create a task and assign it (to themselves or a
teammate); editing/deleting is restricted to the task's owner or a
manager/admin (see `OwnerOrManagerRequiredMixin`), so nobody can quietly
edit someone else's to-do list.
"""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.common.mixins import OwnerOrManagerRequiredMixin
from apps.notifications.services import notify
from apps.tasks.forms import TaskForm
from apps.tasks.models import Task


class TaskListView(LoginRequiredMixin, ListView):
    """The task list: shows owner, due date, status, priority, with a
    one-click "mark done" per row (see `TaskMarkDoneView`) and simple
    GET-parameter filters so the page stays useful as the list grows."""

    model = Task
    context_object_name = "tasks"
    template_name = "tasks/task_list.html"
    paginate_by = 25

    def get_queryset(self):
        qs = Task.objects.select_related("owner", "related_risk", "related_control")

        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)

        if self.request.GET.get("mine") == "1":
            qs = qs.filter(owner=self.request.user)

        return qs.order_by("status", "due_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = Task.Status.choices
        context["current_status"] = self.request.GET.get("status", "")
        context["mine_only"] = self.request.GET.get("mine") == "1"
        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = "task"
    template_name = "tasks/task_detail.html"

    def get_queryset(self):
        return Task.objects.select_related("owner", "related_risk", "related_control")


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Task '{form.instance.title}' created.")
        notify(
            recipient=form.instance.owner,
            message=f"You were assigned a new task: '{form.instance.title}'.",
            link=form.instance.get_absolute_url(),
        )
        return response


class TaskUpdateView(OwnerOrManagerRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def form_valid(self, form):
        previous_owner_id = Task.objects.only("owner_id").get(pk=form.instance.pk).owner_id
        response = super().form_valid(form)
        messages.success(self.request, f"Task '{form.instance.title}' updated.")
        if form.instance.owner_id != previous_owner_id:
            notify(
                recipient=form.instance.owner,
                message=f"You were assigned to task: '{form.instance.title}'.",
                link=form.instance.get_absolute_url(),
            )
        return response


class TaskDeleteView(OwnerOrManagerRequiredMixin, DeleteView):
    model = Task
    template_name = "partials/confirm_delete.html"
    success_url = reverse_lazy("tasks:task_list")

    def form_valid(self, form):
        messages.success(self.request, "Task deleted.")
        return super().form_valid(form)


class TaskMarkDoneView(LoginRequiredMixin, View):
    """POST-only endpoint backing the "Mark done" button on the task
    list — kept as a tiny dedicated view (rather than routing through
    the full update form) so completing a task is a single click."""

    def post(self, request, pk):
        queryset = Task.objects.filter(pk=pk)
        if not request.user.is_manager_or_above:
            queryset = queryset.filter(owner=request.user)

        task = queryset.first()
        if task is None:
            messages.error(request, "You don't have permission to update that task.")
            return self._redirect_back(request)

        task.mark_done()
        messages.success(request, f"Task '{task.title}' marked as done.")
        return self._redirect_back(request)

    @staticmethod
    def _redirect_back(request):
        from django.shortcuts import redirect

        return redirect(request.META.get("HTTP_REFERER") or reverse_lazy("tasks:task_list"))
