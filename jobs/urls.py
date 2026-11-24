from rest_framework.routers import DefaultRouter

from .views import JobViewSet, ProposalViewSet

router = DefaultRouter()
router.register("jobs", JobViewSet, basename="job")
router.register("proposals", ProposalViewSet, basename="proposal")

urlpatterns = router.urls