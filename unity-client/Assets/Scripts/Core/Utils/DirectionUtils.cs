using UnityEngine;

public static class DirectionUtils
{
    public static string GetOpposite(string direction)
    {
        return direction.ToLower() switch
        {
            "north" => "south",
            "south" => "north",
            "east" => "west",
            "west" => "east",
            "up" => "down",
            "down" => "up",
            "northeast" => "southwest",
            "southwest" => "northeast",
            "southeast" => "northwest",
            "northwest" => "southeast",
            _ => direction
        };
    }
}
