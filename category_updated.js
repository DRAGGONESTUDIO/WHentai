// Function to load categories from categories.txt
async function loadCategoriesFromFile() {
    try {
        const response = await fetch('categories.txt');
        const text = await response.text();
        
        // Parse the categories.txt file format (name on one line, count on the next)
        const lines = text.split('\n').map(line => line.trim()).filter(line => line.length > 0);
        const categories = [];
        
        for (let i = 0; i