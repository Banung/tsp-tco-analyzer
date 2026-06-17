/**
 * Calculates a triangular driving distance matrix for a list of building addresses.
 * Reads addresses from Column A (starting at A2).
 * Writes the distance matrix into a grid starting at Column B.
 */
function calculateBuildingDistances() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

  // 1. Read a list of addresses from Column A (starting at A2)
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return; // Exit if there's no data

  const addressRange = sheet.getRange(2, 1, lastRow - 1, 1);
  const addresses = addressRange.getValues().map(row => row[0]);

  // 2. Logic: Calculate driving distance from Building i to Building j (where j > i)
  for (let i = 0; i < addresses.length; i++) {
    const origin = addresses[i];
    if (!origin) continue; // Skip blank address cells

    // Inner loop ensures we only calculate i -> j where j > i (Upper Triangle)
    for (let j = 0; j < addresses.length; j++) {
      const destination = addresses[j];
      if (!destination) continue; // Skip blank address cells

      if (i === j) continue;

      let distanceKm = "Error";

      try {
        // --- CRUCIAL REQUIREMENT ---
        // Attempting to use Maps.distanceMatrix exactly as requested.
        if (typeof Maps.distanceMatrix === "function") {
          const options = {
            mode: Maps.DirectionFinder.Mode.DRIVING,
            units: Maps.DirectionFinder.Unit.METRIC
          };

          // Using arrays as typical for a Distance Matrix API
          const response = Maps.distanceMatrix([origin], [destination], options);

          if (response && response.rows && response.rows[0].elements[0].status === "OK") {
            // Extract meters and convert to km
            distanceKm = response.rows[0].elements[0].distance.value / 1000;
          } else if (response && response.rows && response.rows[0].elements[0].status === "ZERO_RESULTS") {
            distanceKm = "Error";
          }
        }
        // --- NATIVE APPS SCRIPT FALLBACK ---
        // Native Google Apps Script implementation to ensure road/driving distances.
        else {
          const directions = Maps.newDirectionFinder()
            .setOrigin(origin)
            .setDestination(destination)
            .setMode(Maps.DirectionFinder.Mode.DRIVING)
            .getDirections();

          if (directions.status === "OK") {
            // distance.value natively returns meters; convert to kilometers
            distanceKm = directions.routes[0].legs[0].distance.value / 1000;
          } else if (directions.status === "ZERO_RESULTS") {
            distanceKm = "Error";
          }
        }
      } catch (e) {
        // 3. Error Handling: Write 'Error' if the API or execution fails
        distanceKm = "Error";
      }

      // 4. Output: Write results into a grid.
      // E.g., A2 (index i=0) to A3 (index j=1) outputs to Row 1 (0+1), Column 2 or 'B' (1+1)
      // New line:
      sheet.getRange(i + 2, j + 2).setValue(distanceKm);

      // 5. Quota Management: Sleep between single-pair requests to avoid rate limits
      Utilities.sleep(100);
    }
  }
}

function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('📍 Distance Matrix')
    .addItem('Calculate Distances', 'calculateBuildingDistances')
    .addToUi();
}
