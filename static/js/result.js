// Maximize and minimize functionality for charts
document.querySelectorAll('.maximize-btn').forEach(function(btn) {
  btn.addEventListener('click', function() {
    var card = btn.closest('.chart-card');
    var chartHtml = card.querySelector('.chart-container').innerHTML;
    document.getElementById('modal-chart-container').innerHTML = chartHtml;
    document.getElementById('modal').style.display = 'block';
  });
});

document.getElementById('modal-close').addEventListener('click', function() {
  document.getElementById('modal').style.display = 'none';
  document.getElementById('modal-chart-container').innerHTML = '';
});

// Toggle Advanced Insights Section
document.getElementById('toggle-btn').addEventListener('click', function() {
  var section = document.getElementById('charts-section');
  if (section.style.display === 'none' || section.style.display === '') {
    section.style.display = 'block';  // Show section
    this.textContent = 'Hide Advanced Insights';
    // Trigger a window resize event after a short delay to force Plotly to adjust its layout
    setTimeout(function() {
      window.dispatchEvent(new Event('resize'));
    }, 300);
  } else {
    section.style.display = 'none';  // Hide section
    this.textContent = 'Show Advanced Insights';
  }
});