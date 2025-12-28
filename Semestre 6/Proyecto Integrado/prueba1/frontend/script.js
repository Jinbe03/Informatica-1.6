const { jsPDF } = window.jspdf;
let data = [];
let editingId = null;
let currentRole = "corredor";
const tblBody = document.getElementById("tblBody");
const modalForm = new bootstrap.Modal(document.getElementById("modalForm"));
const modalConfirm = new bootstrap.Modal(document.getElementById("modalConfirm"));
const califForm = document.getElementById("califForm");
const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
const auditList = document.getElementById("auditList");
const btnClearAudit = document.getElementById("btnClearAudit");
const csvFileInput = document.getElementById("csvFileInput");

function renderTable() {
  tblBody.innerHTML = "";
  let filtered = data.filter(item => {
    const search = document.getElementById("searchInput").value.toLowerCase();
    const fPeriodo = document.getElementById("filterPeriodo").value;
    const fTipo = document.getElementById("filterTipo").value;
    return (
      (item.empresa.toLowerCase().includes(search) ||
        item.periodo.includes(search) ||
        item.tipo.toLowerCase().includes(search)) &&
      (!fPeriodo || item.periodo === fPeriodo) &&
      (!fTipo || item.tipo === fTipo)
    );
  });
  document.getElementById("dataCount").textContent = `${filtered.length} registro(s)`;
  for (const item of filtered) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${item.empresa}</td>
      <td>${item.periodo}</td>
      <td>${item.tipo}</td>
      <td>${item.calificacion}</td>
      <td>${item.fuente}</td>
      <td>${item.updated}</td>
      <td class="text-end">
        ${currentRole !== "auditor" ? `
        <button class="btn btn-sm btn-outline-primary me-1" onclick="editCalif('${item.id}')">✏️</button>
        ${currentRole === "admin" ? `<button class="btn btn-sm btn-outline-danger" onclick="askDelete('${item.id}')">🗑️</button>` : ""}
        ` : `<span class="text-muted">Sin permisos</span>`}
      </td>
    `;
    tblBody.appendChild(tr);
  }
}

function saveData() {
  localStorage.setItem("nuamData", JSON.stringify(data));
}

function loadData() {
  data = JSON.parse(localStorage.getItem("nuamData") || "[]");
  renderTable();
}

function addAudit(action, details) {
  const now = new Date().toLocaleString();
  const line = document.createElement("div");
  line.textContent = `[${now}] (${currentRole}) ${action} - ${details}`;
  auditList.prepend(line);
  localStorage.setItem("nuamAudit", auditList.innerHTML);
}

function loadAudit() {
  auditList.innerHTML = localStorage.getItem("nuamAudit") || "";
}

function resetForm() {
  califForm.reset();
  editingId = null;
}

document.getElementById("btnNew").onclick = () => {
  resetForm();
  document.getElementById("modalTitle").textContent = "Nueva Calificación";
  modalForm.show();
};

califForm.onsubmit = e => {
  e.preventDefault();
  const item = {
    id: editingId || Date.now().toString(),
    empresa: document.getElementById("empresa").value,
    periodo: document.getElementById("periodo").value,
    tipo: document.getElementById("tipo").value,
    calificacion: document.getElementById("calificacion").value,
    fuente: document.getElementById("fuente").value,
    observaciones: document.getElementById("observaciones").value,
    updated: new Date().toLocaleString()
  };
  if (editingId) {
    data = data.map(d => d.id === editingId ? item : d);
    addAudit("Actualizó", item.empresa);
  } else {
    data.push(item);
    addAudit("Creó", item.empresa);
  }
  saveData();
  renderTable();
  modalForm.hide();
};

window.editCalif = id => {
  const item = data.find(d => d.id === id);
  if (!item) return;
  editingId = id;
  document.getElementById("empresa").value = item.empresa;
  document.getElementById("periodo").value = item.periodo;
  document.getElementById("tipo").value = item.tipo;
  document.getElementById("calificacion").value = item.calificacion;
  document.getElementById("fuente").value = item.fuente;
  document.getElementById("observaciones").value = item.observaciones;
  document.getElementById("modalTitle").textContent = "Editar Calificación";
  modalForm.show();
};

window.askDelete = id => {
  confirmDeleteBtn.onclick = () => {
    data = data.filter(d => d.id !== id);
    saveData();
    renderTable();
    addAudit("Eliminó", id);
    modalConfirm.hide();
  };
  modalConfirm.show();
};

document.getElementById("btnSearch").onclick = renderTable;
document.getElementById("btnReset").onclick = () => {
  document.getElementById("searchInput").value = "";
  document.getElementById("filterPeriodo").value = "";
  document.getElementById("filterTipo").value = "";
  renderTable();
};

document.getElementById("filterPeriodo").onchange = renderTable;
document.getElementById("filterTipo").onchange = renderTable;

document.getElementById("btnExportCSV").onclick = () => {
  let csv = "empresa,periodo,tipo,calificacion,fuente,observaciones,updated\n";
  data.forEach(d => {
    csv += `${d.empresa},${d.periodo},${d.tipo},${d.calificacion},${d.fuente},${d.observaciones},${d.updated}\n`;
  });
  const blob = new Blob([csv], { type: "text/csv" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "calificaciones.csv";
  a.click();
  addAudit("Exportó CSV", `${data.length} registros`);
};

document.getElementById("btnExportPDF").onclick = () => {
  const doc = new jsPDF();
  doc.text("Reporte de Calificaciones Tributarias", 10, 10);
  let y = 20;
  data.forEach(d => {
    doc.text(`${d.empresa} | ${d.periodo} | ${d.tipo} | ${d.calificacion}`, 10, y);
    y += 8;
    if (y > 280) {
      doc.addPage();
      y = 10;
    }
  });
  doc.save("reporte.pdf");
  addAudit("Exportó PDF", `${data.length} registros`);
};

btnClearAudit.onclick = () => {
  auditList.innerHTML = "";
  localStorage.removeItem("nuamAudit");
  addAudit("Limpió auditoría", "");
};

csvFileInput.onchange = e => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = ev => {
    const rows = ev.target.result.split("\n").slice(1);
    rows.forEach(row => {
      const [empresa, periodo, tipo, calificacion, fuente, observaciones] = row.split(",");
      if (empresa && periodo)
        data.push({ id: Date.now().toString() + Math.random(), empresa, periodo, tipo, calificacion, fuente, observaciones, updated: new Date().toLocaleString() });
    });
    saveData();
    renderTable();
    addAudit("Importó CSV", `${rows.length} filas`);
  };
  reader.readAsText(file);
  e.target.value = "";
};

document.getElementById("roleSelect").onchange = e => {
  currentRole = e.target.value;
  document.getElementById("loggedUserDisplay").textContent = `Rol: ${currentRole}`;
  renderTable();
};

document.getElementById("btnLogout").onclick = () => {
  currentRole = "corredor";
  document.getElementById("roleSelect").value = "corredor";
  document.getElementById("loggedUserDisplay").textContent = "";
  renderTable();
  addAudit("Cerró sesión", "");
};

loadData();
loadAudit();
renderTable();
