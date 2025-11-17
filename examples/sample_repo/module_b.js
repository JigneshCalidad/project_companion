// Module B - Sample JavaScript module for testing

/**
 * Formats a date string
 * @param {Date} date - The date to format
 * @returns {string} Formatted date string
 */
function formatDate(date) {
    return date.toISOString().split('T')[0];
}

/**
 * Validates an email address
 * @param {string} email - Email to validate
 * @returns {boolean} True if valid
 */
function validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

class UserManager {
    constructor() {
        this.users = [];
    }

    addUser(user) {
        this.users.push(user);
        return this.users.length;
    }

    findUser(email) {
        return this.users.find(u => u.email === email);
    }

    // TODO: Add user removal functionality
    // FIXME: Handle duplicate emails
}

// Export functions
module.exports = {
    formatDate,
    validateEmail,
    UserManager
};

