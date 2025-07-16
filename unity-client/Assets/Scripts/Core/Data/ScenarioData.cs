using System.Collections.Generic;
using UnityEngine;

public class ScenarioData
{
    public string id;
    public string name;
    public string description;
    public string visualDescription;
    public string narrativeContext;
    public string type;
    public string zone;

    public Texture2D backgroundImage;

    public List<string> characterIds = new();

    public Dictionary<string, string> connectionIdsByDirection = new();
}
