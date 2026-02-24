    class FluentAvatar extends HTMLElement {
        constructor() {
            super();
            const shadow = this.attachShadow({ mode: 'open' });
        }

        connectedCallback() {
            this.render();
        }

        static get observedAttributes() {
            return ['name', 'src', 'size', 'color'];
        }

        attributeChangedCallback() {
            this.render();
        }

        render() {
            const size = this.getAttribute('size') || '32';
            const name = this.getAttribute('name') || '';
            const src = this.getAttribute('src');
            // Fluent UI 默認的品牌藍色
            const color = this.getAttribute('color') || '#0078D4'; 

            // 自動提取姓名首字母 (例如 "John Doe" -> "JD")
            let initials = '';
            if (name) {
                const parts = name.trim().split(' ');
                initials = parts[0][0].toUpperCase();
                if (parts.length > 1) {
                    initials += parts[parts.length - 1][0].toUpperCase();
                }
            }

            this.shadowRoot.innerHTML = `
                <style>
                    :host {
                        display: inline-flex;
                        align-items: center;
                        justify-content: center;
                        width: ${size}px;
                        height: ${size}px;
                        border-radius: 50%;
                        background-color: ${src ? 'transparent' : color};
                        color: white;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        font-size: ${Math.max(10, parseInt(size) / 2.5)}px;
                        font-weight: 600;
                        overflow: hidden;
                        user-select: none;
                        flex-shrink: 0;
                    }
                    img {
                        width: 100%;
                        height: 100%;
                        object-fit: cover;
                    }
                    span {
                        line-height: 1;
                    }
                </style>
                ${src ? `<img src="${src}" alt="${name}">` : `<span>${initials}</span>`}
            `;
        }
    }
    
    // 註冊為自定義元素
    customElements.define('fluent-avatar', FluentAvatar);