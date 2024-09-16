// Display/Hide Specified Content
function toggleContent(show, hide){
    var i;
    for (i = 0; i < show.length; i++) {
        document.getElementById(show[i]).classList.remove("hide");
    }
    for (i = 0; i < hide.length; i++) {
        document.getElementById(hide[i]).classList.add("hide");
    }
}

// Change Display
function change(type) {
    if (type == "users"){
        if (document.getElementById('accounts').value == "everyone"){
            toggleContent(['all-accounts'], ['s-accounts', 'p-accounts', 'c-accounts'])
        }
        else if (document.getElementById('accounts').value == "player-accounts"){
            toggleContent(['s-accounts'], ['all-accounts', 'p-accounts', 'c-accounts'])
        }
        else if (document.getElementById('accounts').value == "parent-accounts"){
            toggleContent(['p-accounts'], ['all-accounts', 's-accounts', 'c-accounts'])
        }
        else if (document.getElementById('accounts').value == "coach-accounts"){
            toggleContent(['c-accounts'], ['all-accounts', 's-accounts', 'p-accounts'])
        }
    }
    else if (type == "sport"){
        if (document.getElementById('Editing').value == "player"){
            toggleContent(['players'], ['coaches', 'year', 'achievements'])
            document.getElementById('name').placeholder="Enter Name";
        }
        else if (document.getElementById('Editing').value == "coach"){
            toggleContent(['coaches'], ['players', 'year', 'achievements'])
            document.getElementById('name').placeholder="Enter Name";
        }
        else if (document.getElementById('Editing').value == "achievements"){
            toggleContent(['year', 'achievements'], ['players', 'coaches'])
            document.getElementById('name').placeholder="Enter Achievement";
        }
    }
    else if (type == "news"){
        if (document.getElementById('Message').value == "event"){
            toggleContent(['events', 'edate', 'sdate', 'edate-label', 'sdate-label'], ['information', 'highlights', 'link'])
            document.getElementById('Message').classList.remove("width-fill");
        }
        else if (document.getElementById('Message').value == "info"){
            toggleContent(['information'], ['events', 'highlights', 'link', 'edate', 'sdate', 'edate-label', 'sdate-label'])
            document.getElementById('Message').classList.add("width-fill");
        }
        else if (document.getElementById('Message').value == "high"){
            toggleContent(['highlights', 'link'], ['events', 'information', 'edate', 'sdate', 'edate-label', 'sdate-label'])
            document.getElementById('Message').classList.add("width-fill");
        }
    }
}

// Edit Information
function edit(tag, id, name, desc, year, link) {
    document.getElementById('cancel').classList.remove("hide");
    document.getElementById('manage').innerHTML = "Save";
    if (tag == "sport"){
        document.getElementById('manage_sport').action = "/manager/sports/" + id;
        document.getElementById('name').value = name;
        document.getElementById('year').value = year;
        document.getElementById('Sport').value = desc;
    }
    else if (tag == "news"){
        document.getElementById('manage_news').action = "/manager/news/" + id;
        document.getElementById('title').value = name;
        document.getElementById('desc').value = desc;
        document.getElementById('link').value = link;
        document.getElementById('sdate').value = year[0].substring(0, 19)
        document.getElementById('edate').value = year[1].substring(0, 19)
    }
    else if (tag == "user"){
        document.getElementById('manage_news').action = "/manager/users/" + id;
        document.getElementById('title').value = name;
        document.getElementById('link').value = link;
    }
}

// Revert Changes
function discard(){
    document.getElementById('cancel').classList.add("hide");
    document.getElementById('manage').innerHTML = "Add";
}