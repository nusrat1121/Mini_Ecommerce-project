let count = 0;

// Add to Cart Function
function addToCart(item, price) {
    count++;
    document.getElementById('cart-count').innerText = count;
    alert(`✨ Success! ${item} added to your bag.\nPrice: ৳{price}`);
}

// Simple Search Logic (Console testing)
const searchInput = document.getElementById('search-input');
searchInput.addEventListener('keyup', (e) => {
    if (e.key === 'Enter') {
        alert("Searching for: " + searchInput.value);
        // Backend e search query pathanor kaj pore hobe
    }
});