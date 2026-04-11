export const isLoggedIn = true;
export const auth = null;
export const currentUser = null;

export function showGlobalMessage(msg, type) {
    console.log(`[${type}] ${msg}`);
}

export function updateNavigation() {
    console.log("Mock updateNavigation called");
}
