// Global state
let allData = [];
let charts = {};

document.addEventListener("DOMContentLoaded", () => {
  fetchData();
  setupEventListeners();
});

async function fetchData() {
  try {
    const response = await fetch("data.json");
    allData = await response.json();

    // Initialize filters
    populateFilters();

    // Initial dashboard update
    updateDashboard();
  } catch (error) {
    console.error("Error loading data:", error);
  }
}

function populateFilters() {
  // Years
  const years = allData.map((d) => d.year).filter((y) => y);
  const minYear = Math.min(...years);
  const maxYear = Math.max(...years);

  document.getElementById("startYear").value = minYear;
  document.getElementById("endYear").value = maxYear;

  // Genres
  const genres = [...new Set(allData.map((d) => d.artist_top_genre))].sort();
  const genreSelect = document.getElementById("genreSelect");
  genres.forEach((g) => {
    const opt = document.createElement("option");
    opt.value = g;
    opt.textContent = g;
    genreSelect.appendChild(opt);
  });

  // Artists
  const artists = [...new Set(allData.map((d) => d.artist))].sort();
  const artistSelect = document.getElementById("artistSelect");
  artists.forEach((a) => {
    const opt = document.createElement("option");
    opt.value = a;
    opt.textContent = a;
    artistSelect.appendChild(opt);
  });
}

function setupEventListeners() {
  document
    .getElementById("applyYear")
    .addEventListener("click", updateDashboard);
  document
    .getElementById("genreSelect")
    .addEventListener("change", updateDashboard);
  document
    .getElementById("artistSelect")
    .addEventListener("change", updateDashboard);
}

function filterData() {
  const startYear = parseInt(document.getElementById("startYear").value) || 0;
  const endYear = parseInt(document.getElementById("endYear").value) || 3000;
  const genre = document.getElementById("genreSelect").value;
  const artist = document.getElementById("artistSelect").value;

  return allData.filter((d) => {
    const yearMatch = d.year >= startYear && d.year <= endYear;
    const genreMatch = genre === "All" || d.artist_top_genre === genre;
    const artistMatch = artist === "All" || d.artist === artist;
    return yearMatch && genreMatch && artistMatch;
  });
}

function updateDashboard() {
  const filtered = filterData();

  updateMetrics(filtered);
  updateCharts(filtered);
  updateTables(filtered);
}

function updateMetrics(data) {
  document.getElementById("totalSongs").textContent = data.length;

  const avgPop =
    data.reduce((sum, d) => sum + (d.popularity || 0), 0) / (data.length || 1);
  document.getElementById("avgPopularity").textContent = avgPop.toFixed(1);

  const avgDance =
    data.reduce((sum, d) => sum + (d.danceability || 0), 0) /
    (data.length || 1);
  document.getElementById("avgDance").textContent = avgDance.toFixed(2);

  // Calc top genre
  if (data.length === 0) {
    document.getElementById("topGenre").textContent = "-";
    return;
  }
  const genreCounts = {};
  data.forEach((d) => {
    genreCounts[d.artist_top_genre] =
      (genreCounts[d.artist_top_genre] || 0) + 1;
  });
  const topGenre = Object.entries(genreCounts).sort(
    (a, b) => b[1] - a[1]
  )[0][0];
  document.getElementById("topGenre").textContent = topGenre;
}

function updateCharts(data) {
  updateTimeChart(data);
  updateGenreChart(data);
  updateScatterChart(data);
  updateRadarChart(data);
}

function updateTimeChart(data) {
  const ctx = document.getElementById("timeChart").getContext("2d");

  // Group by year
  const counts = {};
  data.forEach((d) => {
    counts[d.year] = (counts[d.year] || 0) + 1;
  });
  const sortedYears = Object.keys(counts).sort();
  const values = sortedYears.map((y) => counts[y]);

  if (charts.time) charts.time.destroy();

  charts.time = new Chart(ctx, {
    type: "line",
    data: {
      labels: sortedYears,
      datasets: [
        {
          label: "Songs Released",
          data: values,
          borderColor: "#1DB954",
          backgroundColor: "rgba(29, 185, 84, 0.1)",
          tension: 0.4,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: "#333" } },
        y: { grid: { color: "#333" } },
      },
    },
  });
}

function updateGenreChart(data) {
  const ctx = document.getElementById("genreChart").getContext("2d");

  const counts = {};
  data.forEach((d) => {
    counts[d.artist_top_genre] = (counts[d.artist_top_genre] || 0) + 1;
  });

  const sorted = Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);

  if (charts.genre) charts.genre.destroy();

  charts.genre = new Chart(ctx, {
    type: "bar",
    data: {
      labels: sorted.map((i) => i[0]),
      datasets: [
        {
          label: "Count",
          data: sorted.map((i) => i[1]),
          backgroundColor: "#1DB954",
        },
      ],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: "#333" } },
        y: { grid: { display: false } }, // Hide grid lines on Y for cleaner look
      },
    },
  });
}

function updateScatterChart(data) {
  const ctx = document.getElementById("scatterChart").getContext("2d");

  // Limit points for performance if needed, but 500 is fine
  const points = data.map((d) => ({
    x: d.energy,
    y: d.danceability,
    r: d.popularity / 5, // bubble size
  }));

  if (charts.scatter) charts.scatter.destroy();

  charts.scatter = new Chart(ctx, {
    type: "bubble",
    data: {
      datasets: [
        {
          label: "Songs",
          data: points,
          backgroundColor: "rgba(29, 185, 84, 0.6)",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: {
          title: { display: true, text: "Energy" },
          grid: { color: "#333" },
        },
        y: {
          title: { display: true, text: "Danceability" },
          grid: { color: "#333" },
        },
      },
    },
  });
}

function updateRadarChart(data) {
  const ctx = document.getElementById("radarChart").getContext("2d");

  const features = [
    "danceability",
    "energy",
    "acousticness",
    "instrumentalness",
    "liveness",
    "speechiness",
  ];
  const avgs = features.map((f) => {
    return data.reduce((sum, d) => sum + (d[f] || 0), 0) / (data.length || 1);
  });

  if (charts.radar) charts.radar.destroy();

  charts.radar = new Chart(ctx, {
    type: "radar",
    data: {
      labels: features,
      datasets: [
        {
          label: "Average Profile",
          data: avgs,
          backgroundColor: "rgba(29, 185, 84, 0.4)",
          borderColor: "#1DB954",
          pointBackgroundColor: "#fff",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          angleLines: { color: "#444" },
          grid: { color: "#444" },
          pointLabels: { color: "#ddd" },
          ticks: { display: false },
        },
      },
    },
  });
}

function updateTables(data) {
  // Top Artists
  const artistCounts = {};
  const artistPopSum = {};

  data.forEach((d) => {
    artistCounts[d.artist] = (artistCounts[d.artist] || 0) + 1;
    artistPopSum[d.artist] =
      (artistPopSum[d.artist] || 0) + (d.popularity || 0);
  });

  const sortedArtists = Object.keys(artistCounts)
    .sort((a, b) => artistCounts[b] - artistCounts[a])
    .slice(0, 5);

  const artistTableHtml = sortedArtists
    .map(
      (a) => `
        <tr>
            <td>${a}</td>
            <td>${artistCounts[a]}</td>
            <td>${(artistPopSum[a] / artistCounts[a]).toFixed(1)}</td>
        </tr>
    `
    )
    .join("");

  document.getElementById("topArtistsTable").innerHTML = artistTableHtml;

  // Top Tracks
  const sortedTracks = [...data]
    .sort((a, b) => b.popularity - a.popularity)
    .slice(0, 5);
  const trackTableHtml = sortedTracks
    .map(
      (t) => `
        <tr>
            <td>${t.name}</td>
            <td>${t.artist}</td>
            <td>${t.popularity}</td>
        </tr>
    `
    )
    .join("");

  document.getElementById("topTracksTable").innerHTML = trackTableHtml;
}
