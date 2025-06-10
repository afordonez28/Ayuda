// search.js: Buscador global y pie de página info

async function fetchJson(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error("Error consultando " + url);
    return await res.json();
}

// --- Buscador ---
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("globalSearchForm");
    const resultsDiv = document.getElementById("searchResults");
    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const query = document.getElementById("searchInput").value.trim();
            const searchType = document.getElementById("searchType").value;
            if (!query) {
                resultsDiv.innerHTML = "<div class='search-card'>Por favor escribe algo para buscar.</div>";
                return;
            }
            resultsDiv.innerHTML = "<div class='search-card'>Buscando...</div>";
            try {
                // Si es número, buscar por ID
                if (/^\d+$/.test(query)) {
                    const url = `/api/${searchType}/${query}`;
                    const data = await fetchJson(url);
                    resultsDiv.innerHTML = renderResultCard(data, searchType);
                } else {
                    // Buscar por nombre o característica
                    const q = encodeURIComponent(query);
                    const url = `/api/${searchType}/search/?name=${q}`;
                    const data = await fetchJson(url);
                    if (data.length === 0) {
                        resultsDiv.innerHTML = "<div class='search-card'>No se encontraron resultados.</div>";
                    } else {
                        resultsDiv.innerHTML = data.map(d => renderResultCard(d, searchType)).join("");
                    }
                }
            } catch (err) {
                resultsDiv.innerHTML = `<div class='search-card'>No se encontró ningún elemento.</div>`;
            }
        });
    }

    // --- Footer dinámico ---
    Promise.all([
        fetchJson("/api/planeacion"),
        fetchJson("/api/diseno"),
        fetchJson("/api/objetivo")
    ]).then(([planeacion, diseno, objetivo]) => {
        // Planeación
        const ulPlaneacion = document.getElementById("footerPlaneacionList");
        if (ulPlaneacion) {
            ulPlaneacion.innerHTML = planeacion.map(item =>
                `<li><strong>${item.fase}:</strong> ${item.descripcion}</li>`
            ).join("");
        }
        // Diseño
        const ulDiseno = document.getElementById("footerDisenoList");
        if (ulDiseno) {
            ulDiseno.innerHTML = diseno.map(item =>
                `<li><strong>${item.elemento}:</strong> ${item.descripcion}</li>`
            ).join("");
        }
        // Objetivo
        const objetivoP = document.getElementById("footerObjetivoText");
        if (objetivoP) {
            objetivoP.textContent = objetivo.objetivo;
        }
    });
});

// Renderizar resultado de búsqueda
function renderResultCard(data, type) {
    if (!data) return "";
    let html = `<div class='search-card'><strong>${type === "players" ? "Jugador" : "Enemigo"}:</strong> ${data.name || "(sin nombre)"}<br>`;
    if (type === "players") {
        html += `<b>Salud:</b> ${data.health}, <b>Armadura:</b> ${data.armor}, <b>Velocidad:</b> ${data.speed}`;
    } else {
        html += `<b>Tipo:</b> ${data.type || "N/A"}, <b>Salud:</b> ${data.health}, <b>Velocidad:</b> ${data.speed}`;
    }
    html += "</div>";
    return html;
}