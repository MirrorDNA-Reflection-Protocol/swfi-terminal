const clock = document.getElementById("utc-clock");

function updateClock() {
  if (!clock) return;
  const now = new Date();
  clock.textContent = now.toISOString().slice(11, 19);
}

updateClock();
setInterval(updateClock, 1000);
