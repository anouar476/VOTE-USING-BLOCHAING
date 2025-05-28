// Alert Component
function Alert({ type, message }) {
    const iconMap = {
        success: 'check-circle',
        danger: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    
    return (
        <div className={`alert alert-${type} scale-in`} role="alert">
            <i className={`fas fa-${iconMap[type] || 'info-circle'} me-2`}></i>
            {message}
        </div>
    );
}
