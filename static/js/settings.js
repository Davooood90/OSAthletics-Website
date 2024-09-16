// Webpage Heading
function settings(field){
    document.getElementById('display-settings').classList.toggle("hide");
    document.getElementById('edit-settings').classList.toggle("hide");

    if (field == "name"){
        document.getElementById('title').innerHTML = "Manage Name";
    }
    else if (field == "birthday"){
        document.getElementById('title').innerHTML = "Manage Birthday";
    }
    else if (field == "gender"){
        document.getElementById('title').innerHTML = "Manage Gender";
    }
    else if (field == "phonenum"){
        document.getElementById('title').innerHTML = "Manage Phone Number";
    }
    else if (field == "email"){
        document.getElementById('title').innerHTML = "Manage Email";
    }
    else if (field == "parent"){
        document.getElementById('title').innerHTML = "Manage Parent Email";
    }
    else if (field == "password"){
        document.getElementById('title').innerHTML = "Manage Password";
    }
    else if (field == "recovery"){
        document.getElementById('title').innerHTML = "Manage Recovery Email";
    }

}

// Return
function back(){
    document.getElementById('display-settings').classList.toggle("hide");
    document.getElementById('edit-settings').classList.toggle("hide");
}