import axios from "axios";

const API_BASE = "http://localhost:5000"; // adjust as needed

export const encryptImage = async (file: File, key: string) => {
    const formData = new FormData();
    formData.append("image", file);
    formData.append("key", key);
    const res = await axios.post(`${API_BASE}/encrypt`, formData);
    // Prepend API_BASE to the image_url
    return {
        ...res.data,
        image_url: `${API_BASE}${res.data.image_url}`
    };
};

export const decryptImage = async (file: File, key: string, permutation: number[], keyStream: number[]) => {
    // This function is kept for backward compatibility but now uses the simplified decrypt
    return decryptImageWithoutMetadata(file, key);
};

export const decryptImageWithoutMetadata = async (file: File, key: string) => {
    const formData = new FormData();
    formData.append("image", file);
    formData.append("key", key);

    const res = await axios.post(`${API_BASE}/decrypt`, formData);
    // Prepend API_BASE to the image_url
    return {
        ...res.data,
        image_url: `${API_BASE}${res.data.image_url}`
    };
};

export const analyzeEncryption = async (original: File, encrypted: File) => {
    const formData = new FormData();
    formData.append("original", original);
    formData.append("encrypted", encrypted);
    const res = await axios.post(`${API_BASE}/analyze`, formData);
    return res.data;
};
