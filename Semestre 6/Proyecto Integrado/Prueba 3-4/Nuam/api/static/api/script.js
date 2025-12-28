// ===============================
// ✅ BOOTSTRAP MODALS
// ===============================
const modalForm = new bootstrap.Modal(document.getElementById("modalForm"));
const modalConfirm = new bootstrap.Modal(document.getElementById("modalConfirm"));

let deleteId = null;

// Django envía estos valores:
window.puede_crear = JSON.parse(document.getElementById("djangoPuedeCrear").value);
window.puede_editar = JSON.parse(document.getElementById("djangoPuedeEditar").value);
window.puede_eliminar = JSON.parse(document.getElementById("djangoPuedeEliminar").value);


// ===============================
// ✅ Cargar calificaciones desde Django
// ===============================
function cargarCalificaciones() {
    fetch("/listar_calificaciones/")
    .then(res => res.json())
    .then(data => {
        const tblBody = document.getElementById("tblBody");
        tblBody.innerHTML = "";

        data.forEach(item => {
            tblBody.innerHTML += `
                <tr>
                    <td>${item.empresa}</td>
                    <td>${item.periodo}</td>
                    <td>${item.tipo}</td>
                    <td>${item.calificacion}</td>
                    <td>${item.fuente || ""}</td>
                    <td>${item.created_at ? new Date(item.created_at).toLocaleString() : ""}</td>

                    <td class="text-end">

                        ${window.puede_editar ? `
                            <button class="btn btn-sm btn-warning" onclick="editar(${item.id})">Editar</button>
                        ` : ""}

                        ${window.puede_eliminar ? `
                            <button class="btn btn-sm btn-danger" onclick="confirmarEliminar(${item.id})">Eliminar</button>
                        ` : ""}

                    </td>
                </tr>
            `;
        });
    });
}

cargarCalificaciones();


// ===============================
// ✅ NUEVO: Crear calificación
// ===============================
document.getElementById("btnNew").onclick = () => {
    document.getElementById("califForm").reset();
    document.getElementById("califId").value = "";
    document.getElementById("modalTitle").textContent = "Nueva Calificación";
    modalForm.show();
};


// ===============================
// ✅ Enviar formulario (Crear + Editar)
// ===============================
document.getElementById("califForm").onsubmit = function(e) {
    e.preventDefault();

    const califId = document.getElementById("califId").value;
    const formData = new FormData(this);

    let url = "/guardar_calificacion/";
    if (califId) {
        formData.append("id", califId);
        url = "/guardar_calificacion/?edit=1";
    }

    fetch(url, {
        method: "POST",
        headers: {
            "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
        },
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            modalForm.hide();
            cargarCalificaciones();
        } else {
            alert("Error: " + data.error);
        }
    });
};


// ===============================
// ✅ Editar
// ===============================
window.editar = function(id) {
    fetch("/listar_calificaciones/")
    .then(res => res.json())
    .then(data => {
        const calif = data.find(c => c.id === id);

        if (!calif) return;

        document.getElementById("califId").value = calif.id;
        document.getElementById("empresa").value = calif.empresa;
        document.getElementById("periodo").value = calif.periodo;
        document.getElementById("tipo").value = calif.tipo;
        document.getElementById("calificacion").value = calif.calificacion;
        document.getElementById("fuente").value = calif.fuente || "";
        document.getElementById("observaciones").value = calif.observaciones || "";

        document.getElementById("modalTitle").textContent = "Editar Calificación";
        modalForm.show();
    });
};


// ===============================
// ✅ Eliminar
// ===============================
window.confirmarEliminar = function(id) {
    deleteId = id;
    modalConfirm.show();
};

document.getElementById("confirmDeleteBtn").onclick = () => {
    const csrf = document.querySelector("[name=csrfmiddlewaretoken]").value;

    fetch("/eliminar_calificacion/", {
        method: "POST",
        headers: {
            "X-CSRFToken": csrf,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: `id=${deleteId}`
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            modalConfirm.hide();
            cargarCalificaciones();
        } else {
            alert("Error: " + data.error);
        }
    });
};
