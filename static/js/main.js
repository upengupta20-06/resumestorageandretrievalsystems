/* Global UI helpers shared across pages */

document.addEventListener('DOMContentLoaded', function () {
  // Auto-dismiss alerts after 5 seconds
  document.querySelectorAll('.alert').forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  // Topbar quick search: jump to Search Resumes page with keyword prefilled
  const quickSearch = document.getElementById('quickSearch');
  if (quickSearch) {
    quickSearch.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && quickSearch.value.trim()) {
        window.location.href = `/search-resumes?keyword=${encodeURIComponent(quickSearch.value.trim())}`;
      }
    });
  }
});
