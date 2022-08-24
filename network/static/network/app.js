document.addEventListener('DOMContentLoaded', function () {
    
    // Open and close menu for mobile
    const nav = document.querySelector("nav");
    const nav_btn = document.querySelector("#nav-menu-btn");
    const nav_links = document.querySelector(".nav-links");

    

    nav_btn.addEventListener('click', function () {
        nav_links.classList.add('active');
        const menu_expanded = JSON.parse(nav_btn.getAttribute('aria-expanded'));
        nav_btn.setAttribute('aria-expanded', !menu_expanded);
        !menu_expanded && nav.classList.add('activated');
    });
    
    if (document.getElementById('user-profile') && document.getElementById('followee-id')) {
        const followers = JSON.parse(document.getElementById('user-profile').textContent);
        const followee_id = JSON.parse(document.getElementById('followee-id').textContent);
        // check if profile page is not own
        if (followers.uid !== followee_id) {
            // set follow or unfollow initial state
            check_follow = followers.followers.some(el => el.id === followee_id)
            if (check_follow === true) {
                document.getElementById('follow').style.display = 'none';
                document.getElementById('unfollow').style.display = 'block';
            }
            else {
                document.getElementById('follow').style.display = 'block';
                document.getElementById('unfollow').style.display = 'none';
            }

            // Follow user upon button press
            document.querySelector('#follow').addEventListener('click', function () {
                follow_handle(followee_id);
                this.style.display = 'none';
                document.getElementById('unfollow').style.display = 'block';
            });
            document.querySelector('#unfollow').addEventListener('click', function () {
                follow_handle(followee_id);
                this.style.display = 'none';
                document.getElementById('follow').style.display = 'block';
            });            

        }
    }

    // Add Random Profile Pictures
    if (document.querySelector("#profile-img")) {
        document.querySelectorAll("#profile-img").forEach(img => {
            const genderArray = ['male', 'female'];
            var arrayIndex = Math.round(getRandomArbitrary(0, 1))
            img.src = `https://xsgames.co/randomusers/assets/avatars/${genderArray[arrayIndex]}/${Math.round(getRandomArbitrary(0, 78))}.jpg`;
        })
    }


    // Check if user is on post-editable page
    if (document.querySelector(".popuptrigger")) {
        let edit_buttons = document.querySelectorAll(".popuptrigger");
        edit_buttons.forEach(function (el) {
            el.addEventListener('click', function (e) {
                e.preventDefault();
                // Display popup to allow user to edit
                document.querySelector('.popup').style.display = "flex";

                // Remove popup if user clicks back button
                document.getElementById("back-button").addEventListener('click', function () {
                    document.querySelector(".popup").style.display = "none";
                })

                // Populate edit form with user's post
                populate_edit(el.dataset.id)

                // Send edited information to database when user clicks 'edit'
                document.getElementById("edit-button").onclick = function () {
                    edited_content = document.getElementById("edit-text").value
                    edit_post(el.dataset.id)
                    // Remove popup
                    document.querySelector(".popup").style.display = "none"
                    
                    // Replace old text with edited text without reload
                    var edited_post = document.querySelector(`[data-post-id="${el.dataset.id}"]`)
                    edited_post.querySelector(".post-content").textContent = edited_content
                };
            })
        })
    }

    // Check if user is on page with like functionality
    if (document.querySelector(".post-likes")) {
        let like_buttons = document.querySelectorAll(".like")
        let unlike_buttons = document.querySelectorAll(".unlike")
        get_likes()
        like_buttons.forEach(function (el) {
            // On click like a post
            el.addEventListener('click', function (e) {
                e.preventDefault();
                post_id = el.parentNode.parentNode.parentNode.dataset.postId;
                handle_like(post_id);
                // Update like count and like button without refresh
                el.style.display = "none";
                el.parentNode.querySelector(".unlike").style.display = "flex";
                like_count = el.parentNode.querySelector(".like-count");
                like_count.innerHTML = parseInt(like_count.innerHTML) + 1;
            })
        })
        unlike_buttons.forEach(function (el) {
            // On click unlike a post
            el.addEventListener('click', function (e) {
                e.preventDefault();
                post_id = el.parentNode.parentNode.parentNode.dataset.postId;
                handle_unlike(post_id);
                // Update like count and unlike button without refresh
                el.style.display = "none";
                el.parentNode.querySelector(".like").style.display = "flex";
                like_count = el.parentNode.querySelector(".like-count");
                like_count.innerHTML = parseInt(like_count.innerHTML) - 1;
            })
        })
    }




});

// Functions

function getRandomArbitrary(min, max) {
    return Math.random() * (max - min) + min;
}

function follow_handle(uid) {
    // Follow or unfollow a user
    fetch(`/follow/${uid}/`, {
        method: 'PUT',
        body: JSON.stringify({
            followers: true
        })
    })
    .then(response => response.json())
    .catch((error) => {
        console.error('Error:', error);
    });
}

function populate_edit(post_id) {
    // Populates the text area
    fetch(`/edit/${post_id}/`,)
        .then(response => response.json())
        .then(post => {
            document.getElementById("edit-text").value = post.content;
        })
        .catch((err) => console.log(err));
}

function edit_post(post_id) {
    // Edits the post
    fetch(`/edit/${post_id}/`, {
        method: 'PUT',
        body: JSON.stringify({
            content: document.getElementById("edit-text").value,
        })
    })
        .then(response => response.json())
        .catch(err => {
            console.log(err);
        })
}

function get_likes() {
    // Retrieves like information
    window.onload = function () {
        // Displays like icon by default
        var posts = document.querySelectorAll(".post");
        posts.forEach(function (el) {
            el.querySelector(".like").style.display = "flex";
            el.querySelector(".unlike").style.display = "none";
        });        
        fetch("/likes/")
            .then(response => response.json())
            .then(likes => {
                likes.forEach(like => {
                    // Displays unlike icon if post is already liked
                    if (like.liked === true) {
                        var liked_post = document.querySelector(`[data-post-id="${like.id}"]`)
                        if (liked_post) {
                            liked_post.querySelector(".like").style.display = "none";
                            liked_post.querySelector(".unlike").style.display = "flex";
                        }
                    }
                });
            });
        }
}

function handle_like(post_id) {
    // Sends like/unlike data to the server
    fetch(`/like/${post_id}/`, {
        method: 'PUT',
        body: JSON.stringify({
            liked: true
        })
    })
    .then(response => response.json())
    .catch(err => {
        console.log(err);
    })
}

function handle_unlike(post_id) {
    // Sends like/unlike data to the server
    fetch(`/like/${post_id}/`, {
        method: 'PUT',
        body: JSON.stringify({
            liked: false
        })
    })
    .then(response => response.json())
    .catch(err => console.log(err))
}