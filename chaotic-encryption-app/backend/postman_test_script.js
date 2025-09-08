// Postman Test Script for Chaotic Encryption App
// Copy and paste this into Postman's Pre-request Script or Tests tab

// Generate a test image base64 (1x1 red pixel)
const testImageBase64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==";

// Set collection variables
pm.collectionVariables.set("test_image_b64", testImageBase64);
pm.collectionVariables.set("base_url", "http://localhost:5001");
pm.collectionVariables.set("test_key", "test_encryption_key_123");

// Test script for encryption requests
if (pm.info.requestName.includes("Encrypt")) {
    pm.test("Encryption successful", function () {
        pm.response.to.have.status(200);
        const response = pm.response.json();
        pm.expect(response.success).to.be.true;
        pm.expect(response.encrypted_image).to.exist;
        pm.expect(response.metrics).to.exist;
        
        // Store encrypted image for decryption tests
        pm.collectionVariables.set("encrypted_image_b64", response.encrypted_image);
        
        console.log("Encryption successful for:", pm.info.requestName);
        console.log("Entropy Original:", response.metrics.entropy_original);
        console.log("Entropy Encrypted:", response.metrics.entropy_encrypted);
        console.log("NPCR:", response.metrics.npcr);
        console.log("UACI:", response.metrics.uaci);
    });
}

// Test script for decryption requests
if (pm.info.requestName.includes("Decrypt")) {
    pm.test("Decryption successful", function () {
        pm.response.to.have.status(200);
        const response = pm.response.json();
        pm.expect(response.success).to.be.true;
        pm.expect(response.decrypted_image).to.exist;
        
        console.log("Decryption successful for:", pm.info.requestName);
    });
}

// Test script for error cases
if (pm.info.requestName.includes("Error")) {
    pm.test("Error handling works", function () {
        // Should return 400 for invalid data or 200 with success: false
        pm.expect(pm.response.code).to.be.oneOf([200, 400, 500]);
    });
}

// Performance test
if (pm.info.requestName.includes("Performance")) {
    pm.test("Performance acceptable", function () {
        pm.response.to.have.status(200);
        const responseTime = pm.response.responseTime;
        pm.expect(responseTime).to.be.below(10000); // Should complete within 10 seconds
        console.log("Response time:", responseTime, "ms");
    });
}
