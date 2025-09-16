let editedData = {}; 

document.addEventListener("DOMContentLoaded", fetchData);

function fetchData() {
    eel.get_items()(function(data) {
        const items = JSON.parse(data);
        const tbody = document.querySelector("#barcodeTable tbody");
        tbody.innerHTML = "";
        //<td>${item.barcode}</td> put it under <tr data-itemid="${item.item_id}">
        //if you want to see the barcode too on the Table 
        items.forEach(item => {
            const row = `<tr data-itemid="${item.item_id}">
                <td contenteditable="true" oninput="trackChanges('${item.item_id}', 'box_name', this)">${item.box_name}</td>
                <td contenteditable="true" oninput="trackChanges('${item.item_id}', 'product_name', this)">${item.product_name}</td>
                <td contenteditable="true" oninput="trackChanges('${item.item_id}', 'quantity', this)">${item.quantity}</td>
                <td contenteditable="true" oninput="trackChanges('${item.item_id}', 'expiration_date', this)">${item.expiration_date}</td>
                <td contenteditable="true" oninput="trackChanges('${item.item_id}', 'count', this)">${item.count}</td>
                <td><img src="${item.image ? 'data:image/png;base64,' + item.image : 'placeholder.jpg'}" width="50"></td>
                <td><button onclick="deleteItem('${item.item_id}')">Delete</button></td>
            </tr>`;
            tbody.innerHTML += row;
        });
    });
}

function trackChanges(item_id, field, element) {
    if (!editedData[item_id]) editedData[item_id] = {};
    editedData[item_id][field] = element.innerText;
}

function saveChanges() {
    for (let item_id in editedData) {
        for (let field in editedData[item_id]) {
            eel.update_item(parseInt(item_id), field, editedData[item_id][field])(function(response) {
                console.log(response);
            });
        }
    }
    alert("Changes saved!");
    editedData = {};
    fetchData();
}



function deleteItem(item_id) {
    eel.delete_item(parseInt(item_id))(function(response) {
        console.log(response);
        fetchData();
    });
}

function searchTable() {
    let searchQuery = document.getElementById("search").value.toLowerCase();
    let rows = document.querySelectorAll("#barcodeTable tbody tr");

    rows.forEach(row => {
        let text = row.innerText.toLowerCase();
        row.style.display = text.includes(searchQuery) ? "" : "none";
    });
}


