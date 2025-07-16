using System;
using UnityEngine;

namespace Api.Models
{
    /// <summary>
    /// Model representing the response from the /generate/status endpoint.
    /// </summary>
    [Serializable]
    public class GenerationStatus
    {
        public string status;    // "idle", "running", "done", "error"
        public float progress;   // Value between 0.0 and 1.0
        public string message;   // Current message (e.g., "Generating map...")
        public string detail;    // Additional details (e.g., "You can poll /generate/status...")
    }
}
