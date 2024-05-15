import { toast } from "react-hot-toast";

// Success toast
export const successToast = (message: string) => {
  toast.success(message, {
    position: "top-right",
    duration: 3000,
    style: {
      border: "2px solid #10B981",
      padding: "16px",
      color: "#10B981",
      backgroundColor: "#ECFDF5",
      borderRadius: "8px",
    },
  });
};

// Completion toast
export const completionToast = (message: string) => {
  toast(message, {
    position: "top-center",
    duration: 3000,

    style: {
      border: "2px solid #6B7280",
      padding: "16px",
      color: "#6B7280",
      backgroundColor: "#F3F4F6",
      borderRadius: "8px",
    },
  });
};

// Error toast
export const errorToast = (message: string) => {
  toast.error(message, {
    position: "top-right",
    duration: 3000,
    style: {
      border: "2px solid #EF4444",
      padding: "16px",
      color: "#EF4444",
      backgroundColor: "#FEE2E2",
      borderRadius: "8px",
    },
  });
};
