using UnityEngine;
using UnityEditor;
using System.Collections.Generic;

public class LevelGeneratorWindow : EditorWindow
{
    int roomCount = 5;
    int seed = 42;
    float roomSpacing = 20f;
    bool hasBossRoom = true;
    bool hasTreasureRoom = false;
    GameObject roomPrefab;
    string jsonFileName = "kushal_test";

    [MenuItem("LevelGen/Open Generator")]
    public static void ShowWindow()
    {
        GetWindow<LevelGeneratorWindow>("Level Generator");
    }

    void OnGUI()
    {
        GUILayout.Label("Layout Settings", EditorStyles.boldLabel);

        roomPrefab = (GameObject)EditorGUILayout.ObjectField(
            "Room Prefab", roomPrefab, typeof(GameObject), false);

        roomCount = EditorGUILayout.IntSlider("Room Count", roomCount, 2, 20);
        seed = EditorGUILayout.IntField("Seed", seed);
        roomSpacing = EditorGUILayout.FloatField("Room Spacing", roomSpacing);
        hasBossRoom = EditorGUILayout.Toggle("Include Boss Room", hasBossRoom);
        hasTreasureRoom = EditorGUILayout.Toggle("Include Treasure Room", hasTreasureRoom);

        GUILayout.Space(10);
        GUILayout.Label("Load from Kushal's AI", EditorStyles.boldLabel);
        jsonFileName = EditorGUILayout.TextField("JSON File Name", jsonFileName);

        if (GUILayout.Button("Load from JSON"))
            LoadFromJSON();

        GUILayout.Space(5);

        if (GUILayout.Button("Generate Layout"))
            GenerateLayout();

        if (GUILayout.Button("Clear Layout"))
            ClearLayout();
    }

    void LoadFromJSON()
    {
        if (roomPrefab == null)
        {
            EditorUtility.DisplayDialog("Error", "Please assign a Room Prefab first!", "OK");
            return;
        }

        string path = Application.streamingAssetsPath + "/" + jsonFileName + ".json";

        if (!System.IO.File.Exists(path))
        {
            EditorUtility.DisplayDialog("Error", "File not found: " + path, "OK");
            return;
        }

        string json = System.IO.File.ReadAllText(path);
        LevelLoader.LevelData level = JsonUtility.FromJson<LevelLoader.LevelData>(json);

        if (level == null || level.rooms == null)
        {
            EditorUtility.DisplayDialog("Error", "Invalid JSON format!", "OK");
            return;
        }

        ClearLayout();

        // Calculate positions based on connections
        Vector3[] positions = new Vector3[level.rooms.Count];
        bool[] positioned = new bool[level.rooms.Count];
        int[] childCount = new int[level.rooms.Count];

        positions[0] = Vector3.zero;
        positioned[0] = true;

        Vector3[] directions = new Vector3[]
        {
            new Vector3(roomSpacing, 0, 0),
            new Vector3(0, 0, -roomSpacing),
            new Vector3(-roomSpacing, 0, 0),
            new Vector3(0, 0, roomSpacing),
        };

        if (level.connections != null)
        {
            foreach (var conn in level.connections)
            {
                int from = conn.from;
                int to = conn.to;

                if (!positioned[to])
                {
                    int dir = childCount[from] % directions.Length;
                    positions[to] = positions[from] + directions[dir];
                    positioned[to] = true;
                    childCount[from]++;
                }
            }
        }

        // Spawn rooms
        for (int i = 0; i < level.rooms.Count; i++)
        {
            GameObject room = (GameObject)PrefabUtility.InstantiatePrefab(roomPrefab);
            room.transform.position = positions[i];
            room.transform.localScale = new Vector3(0.5f, 0.5f, 0.5f);
            room.name = level.rooms[i].type + "_" + i;

            Renderer rend = room.GetComponentInChildren<Renderer>();
            if (rend != null)
            {
                rend.sharedMaterial = new Material(rend.sharedMaterial);
                rend.sharedMaterial.color = GetRoomColor(level.rooms[i].type);
            }

            Undo.RegisterCreatedObjectUndo(room, "Load Room");
            Debug.Log("Room " + i + ": " + level.rooms[i].type +
                      " at " + positions[i] +
                      " | Mood: " + level.rooms[i].mood);
        }

        // Draw connection lines
        if (level.connections != null)
        {
            foreach (var conn in level.connections)
            {
                int from = conn.from;
                int to = conn.to;
                GameObject lineObj = new GameObject("connection_" + from + "_" + to);
                LineRenderer lr = lineObj.AddComponent<LineRenderer>();
                lr.startWidth = 0.3f;
                lr.endWidth = 0.3f;
                lr.positionCount = 2;
                lr.SetPosition(0, positions[from] + Vector3.up);
                lr.SetPosition(1, positions[to] + Vector3.up);
                lr.material = new Material(Shader.Find("Sprites/Default"));
                lr.startColor = Color.cyan;
                lr.endColor = Color.cyan;

                Undo.RegisterCreatedObjectUndo(lineObj, "Connection Line");
            }
        }

        Debug.Log("Level loaded: " + jsonFileName);
    }

    void GenerateLayout()
    {
        if (roomPrefab == null)
        {
            EditorUtility.DisplayDialog("Error", "Please assign a Room Prefab first!", "OK");
            return;
        }

        ClearLayout();
        Random.InitState(seed);

        List<string> layout = new List<string>();
        layout.Add("entrance");

        for (int i = 1; i < roomCount - 1; i++)
        {
            if (hasTreasureRoom && i == roomCount / 2)
                layout.Add("treasure");
            else
                layout.Add(Random.value > 0.5f ? "standard" : "corridor");
        }

        layout.Add(hasBossRoom ? "boss" : "standard");

        for (int i = 0; i < layout.Count; i++)
        {
            Vector3 pos = new Vector3(i * roomSpacing, 0, 0);
            GameObject room = (GameObject)PrefabUtility.InstantiatePrefab(roomPrefab);
            room.transform.position = pos;
            room.name = layout[i] + "_" + i;

            Renderer rend = room.GetComponentInChildren<Renderer>();
            if (rend != null)
            {
                rend.sharedMaterial = new Material(rend.sharedMaterial);
                rend.sharedMaterial.color = GetRoomColor(layout[i]);
            }

            Undo.RegisterCreatedObjectUndo(room, "Generate Room");
        }

        Debug.Log("Generated " + layout.Count + " rooms with seed: " + seed);
    }

    void ClearLayout()
    {
        GameObject[] allObjects = FindObjectsByType<GameObject>(FindObjectsSortMode.None);
        foreach (GameObject obj in allObjects)
        {
            if (obj.name.Contains("entrance") || obj.name.Contains("standard") ||
                obj.name.Contains("corridor") || obj.name.Contains("treasure") ||
                obj.name.Contains("boss") || obj.name.Contains("connection_"))
            {
                Undo.DestroyObjectImmediate(obj);
            }
        }
    }

    Color GetRoomColor(string type)
    {
        switch (type)
        {
            case "entrance": return Color.green;
            case "boss":     return Color.red;
            case "treasure": return Color.yellow;
            case "corridor": return Color.grey;
            default:         return Color.white;
        }
    }
}