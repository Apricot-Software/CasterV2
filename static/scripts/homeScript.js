let currentPage = -1;
let isLoading = false;

function loadPosts() {
    if (isLoading) return;
    isLoading = true;

    currentPage++;
    fetch(`/api/posts?page=${currentPage}`)
        .then(response => response.json())
        .then(posts => {
            const postsFlexBox = document.getElementById('post-flex-box');
            posts.forEach(post => {
                const postContainer = document.createElement('div');
                postContainer.className = 'post-container';
                postContainer.onclick = function(){ window.location.href = `/post?id=${post.postId}`; };

                const userBar = document.createElement('p');
                const contentDiv = document.createElement('div')
                userBar.className = 'user-bar';
                contentDiv.appendChild(userBar);


                const userpfp = document.createElement('img');
                userpfp.src = post.pfp;
                userpfp.className = 'user-pfp';
                postContainer.appendChild(userpfp);

                const displayName = document.createElement('a');
                displayName.innerText = post.displayName;
                displayName.className = 'display-name';
                displayName.href = post.handle.replace('@', '')
                userBar.appendChild(displayName);

                if (post.isveri) {
                   const checkmark = document.createElement('img');
                   checkmark.src = 'static/img/veri.png';
                   checkmark.style.width = '15px';
                   userBar.appendChild(checkmark);
                };


                const handle = document.createElement('span');
                handle.innerText = `${post.handle} • ${post.timestamp}`;
                handle.className = 'handle';
                userBar.appendChild(handle);
                postContainer.appendChild(contentDiv);

                const postContent = document.createElement('p');
                postContent.innerHTML = `${post.postContent}`;
                postContent.className = 'post-text';
                contentDiv.appendChild(postContent);

                const actionBar = document.createElement('div');
                actionBar.className = 'post-action-bar';
                contentDiv.appendChild(actionBar);

                // Like action
                const likeContainer = document.createElement('span');
                actionBar.appendChild(likeContainer);

                const likeIcon = document.createElement('img');
                likeIcon.src = 'static/img/like-unselect.png';
                likeIcon.className = 'like-icon';
                likeContainer.appendChild(likeIcon);

                const likeCounter = document.createElement('a');
                likeCounter.innerText = post.likes || '0';
                likeCounter.className = 'ab-text';
                likeContainer.appendChild(likeCounter);

                // Comment action
                const commentContainer = document.createElement('span');
                actionBar.appendChild(commentContainer);

                const commentIcon = document.createElement('img');
                commentIcon.src = 'static/img/message.png';
                commentIcon.className = 'like-icon';
                commentContainer.appendChild(commentIcon);

                const commentCounter = document.createElement('a');
                commentCounter.innerText = post.replys || '0';
                commentCounter.className = 'ab-text';
                commentContainer.appendChild(commentCounter);

                // Share action
                const shareContainer = document.createElement('span');
                actionBar.appendChild(shareContainer);

                const shareIcon = document.createElement('img');
                shareIcon.src = 'static/img/share.png';
                shareIcon.className = 'like-icon';
                shareContainer.appendChild(shareIcon);

                const shareCounter = document.createElement('a');
                shareCounter.innerText = post.shares || '0';
                shareCounter.className = 'ab-text';
                shareContainer.appendChild(shareCounter);

                postsFlexBox.appendChild(postContainer);
            });

            isLoading = false;

        })
        .catch(error => console.error('Error fetching data:', error));
}

function loadSearchPosts() {

    const searchInput = document.getElementById('searchInput').value;


    fetch(`/api/searchposts?query=${searchInput}`)
        .then(response => response.json())
        .then(posts => {
            const postsFlexBox = document.getElementById('search-post-flex-box');
            postsFlexBox.innerHTML = "";
            posts.forEach(post => {
                const postContainer = document.createElement('div');
                postContainer.className = 'post-container';
                postContainer.onclick = function(){ window.location.href = `/post?id=${post.postId}`; };

                const userBar = document.createElement('p');
                const contentDiv = document.createElement('div')
                userBar.className = 'user-bar';
                contentDiv.appendChild(userBar);


                const userpfp = document.createElement('img');
                userpfp.src = post.pfp;
                userpfp.className = 'user-pfp';
                postContainer.appendChild(userpfp);

                const displayName = document.createElement('a');
                displayName.innerText = post.displayName;
                displayName.className = 'display-name';
                displayName.href = post.handle.replace('@', '')
                userBar.appendChild(displayName);

                if (post.isveri) {
                   const checkmark = document.createElement('img');
                   checkmark.src = 'static/img/veri.png';
                   checkmark.style.width = '15px';
                   userBar.appendChild(checkmark);
                };


                const handle = document.createElement('span');
                handle.innerText = `${post.handle} • ${post.timestamp}`;
                handle.className = 'handle';
                userBar.appendChild(handle);
                postContainer.appendChild(contentDiv);

                const postContent = document.createElement('p');
                postContent.innerHTML = `${post.postContent}`;
                postContent.className = 'post-text';
                contentDiv.appendChild(postContent);

                const actionBar = document.createElement('div');
                actionBar.className = 'post-action-bar';
                contentDiv.appendChild(actionBar);

                // Like action
                const likeContainer = document.createElement('span');
                actionBar.appendChild(likeContainer);

                const likeIcon = document.createElement('img');
                likeIcon.src = 'static/img/like-unselect.png';
                likeIcon.className = 'like-icon';
                likeContainer.appendChild(likeIcon);

                const likeCounter = document.createElement('a');
                likeCounter.innerText = post.likes || '0';
                likeCounter.className = 'ab-text';
                likeContainer.appendChild(likeCounter);

                // Comment action
                const commentContainer = document.createElement('span');
                actionBar.appendChild(commentContainer);

                const commentIcon = document.createElement('img');
                commentIcon.src = 'static/img/message.png';
                commentIcon.className = 'like-icon';
                commentContainer.appendChild(commentIcon);

                const commentCounter = document.createElement('a');
                commentCounter.innerText = post.replys || '0';
                commentCounter.className = 'ab-text';
                commentContainer.appendChild(commentCounter);

                // Share action
                const shareContainer = document.createElement('span');
                actionBar.appendChild(shareContainer);

                const shareIcon = document.createElement('img');
                shareIcon.src = 'static/img/share.png';
                shareIcon.className = 'like-icon';
                shareContainer.appendChild(shareIcon);

                const shareCounter = document.createElement('a');
                shareCounter.innerText = post.shares || '0';
                shareCounter.className = 'ab-text';
                shareContainer.appendChild(shareCounter);

                postsFlexBox.appendChild(postContainer);
            });

            isLoading = false;

        })
        .catch(error => console.error('Error fetching data:', error));
}

    document.addEventListener('DOMContentLoaded', loadPosts);

    const mainContent = document.querySelector('.main-content');


    mainContent.addEventListener('scroll', function() {
        if (mainContent.scrollTop + mainContent.clientHeight >= mainContent.scrollHeight - 1700) {
            console.log(mainContent.scrollTop + mainContent.clientHeight >= mainContent.scrollHeight - 100);
            loadPosts();
        }
    });


document.addEventListener('DOMContentLoaded', loadPosts);