// View/src/api.js
export async function getCarRecommendations(userInput) {
  try {
    const response = await fetch("http://localhost:5001/api/search", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query: userInput }),
    });

    if (!response.ok) throw new Error("Failed to fetch recommendations");

    const data = await response.json();
    return data; // Adjust based on backend response structure
  } catch (err) {
    console.error(err);
    return [];
  }
}
