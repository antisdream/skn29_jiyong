document.addEventListener('DOMContentLoaded', () => {
    const todoListContainer = document.getElementById('spa-todo-list');
    const todoForm = document.getElementById('spa-todo-form');
    const titleInput = document.getElementById('spa-title');
    const contentInput = document.getElementById('spa-content');
    const imageInput = document.getElementById('spa-image');

    const statTotal = document.getElementById('stat-total');
    const statPending = document.getElementById('stat-pending');
    const statCompleted = document.getElementById('stat-completed');
    const statRate = document.getElementById('stat-rate');

    const updateDashboard = (todos) => {
        const total = todos.length;
        const completed = todos.filter(todo => todo.is_completed).length;
        const pending = total - completed;
        const rate = total > 0 ? Math.round((completed / total) * 100) : 0;

        if (statTotal) statTotal.innerText = total;
        if (statPending) statPending.innerText = pending;
        if (statCompleted) statCompleted.innerText = completed;
        if (statRate) statRate.innerText = `${rate}%`;
    };

    const getRelativeTimeString = (dateInput) => {
        const date = new Date(dateInput);
        const now = new Date();
        const diffMs = now - date;
        const diffSec = Math.floor(diffMs / 1000);

        if (diffSec < 0) return '방금 전';

        const diffMin = Math.floor(diffSec / 60);
        const diffHour = Math.floor(diffMin / 60);
        const diffDay = Math.floor(diffHour / 24);

        if (diffMin < 1) {
            return '방금 전';
        }
        if (diffMin < 60) {
            return `${diffMin}분 전`;
        }
        if (diffHour < 24) {
            return `${diffHour}시간 전`;
        }
        if (diffDay < 7) {
            return `${diffDay}일 전`;
        }

        return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    };

    const loadTodos = async () => {
        try {
            const response = await fetch(apiBaseUrl, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            });
            if (!response.ok) throw new Error('목록 조회 실패');

            const todos = await response.json();
            renderTodos(todos);
            updateDashboard(todos);
        } catch (error) {
            console.error(error);
            todoListContainer.innerHTML = `
                <div class="empty-state">
                    <p style="color: #ef4444;">데이터를 불러오는 중 오류가 발생했습니다.</p>
                </div>
            `;
        }
    };

    const renderTodos = (todos) => {
        if (todos.length === 0) {
            todoListContainer.innerHTML = `
                <div class="empty-state">
                    <p>등록된 할일이 없습니다. 새 할일을 비동기로 추가해 보세요.</p>
                </div>
            `;
            return;
        }

        todoListContainer.innerHTML = '';

        todos.forEach((todo, index) => {
            const card = document.createElement('div');
            const rowClass = index % 2 === 0 ? 'card-even' : 'card-odd';
            card.className = `todo-card ${todo.is_completed ? 'completed' : ''} ${rowClass}`;
            const dateString = getRelativeTimeString(todo.created_at);

            card.innerHTML = `
                <div class="todo-card-header">
                    <button class="status-badge btn-toggle" data-id="${todo.id}" data-completed="${todo.is_completed}" style="border: none; cursor: pointer;">
                        ${todo.is_completed ? '완료' : '대기중'}
                    </button>
                    <span class="todo-date">${dateString}</span>
                </div>
                <h3 class="todo-title">${todo.title}</h3>
                ${todo.content ? `<p class="todo-body">${todo.content}</p>` : ''}
                ${todo.image ? `<img src="${todo.image}" alt="${todo.title}" class="todo-image">` : ''}
                <div class="todo-actions">
                    <button class="btn-text btn-delete-spa" data-id="${todo.id}" style="color: #ef4444;">삭제</button>
                </div>
            `;
            todoListContainer.appendChild(card);
        });

        attachCardListeners();
    };

    const attachCardListeners = () => {
        document.querySelectorAll('.btn-delete-spa').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const todoId = e.target.getAttribute('data-id');
                if (!confirm('이 할일을 비동기로 삭제하시겠습니까?')) return;

                try {
                    const response = await fetch(`${apiBaseUrl}${todoId}/`, {
                        method: 'DELETE',
                        headers: {
                            'X-CSRFToken': csrfToken
                        }
                    });
                    if (response.ok) {
                        loadTodos();
                    } else {
                        alert('삭제에 실패했습니다.');
                    }
                } catch (error) {
                    console.error(error);
                    alert('삭제 중 통신 에러 발생');
                }
            });
        });

        document.querySelectorAll('.btn-toggle').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const todoId = e.target.getAttribute('data-id');
                const isCompleted = e.target.getAttribute('data-completed') === 'true';

                try {
                    const response = await fetch(`${apiBaseUrl}${todoId}/`, {
                        method: 'PATCH',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({ is_completed: !isCompleted })
                    });
                    if (response.ok) {
                        loadTodos();
                    } else {
                        alert('상태 갱신에 실패했습니다.');
                    }
                } catch (error) {
                    console.error(error);
                    alert('상태 갱신 중 통신 에러 발생');
                }
            });
        });
    };

    todoForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const title = titleInput.value.trim();
        const content = contentInput.value.trim();

        if (!title) return;

        const formData = new FormData();
        formData.append('title', title);
        formData.append('content', content);
        formData.append('is_completed', 'false');
        if (imageInput.files.length > 0) {
            formData.append('image', imageInput.files[0]);
        }

        try {
            const response = await fetch(apiBaseUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                body: formData
            });

            if (response.ok) {
                titleInput.value = '';
                contentInput.value = '';
                imageInput.value = '';
                loadTodos();
            } else {
                const errors = await response.json();
                alert(`저장 실패: ${JSON.stringify(errors)}`);
            }
        } catch (error) {
            console.error(error);
            alert('저장 중 통신 에러 발생');
        }
    });

    loadTodos();
});
