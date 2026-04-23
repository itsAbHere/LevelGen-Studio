using UnityEngine;
using UnityEditor;
using System.Collections.Generic;

public class LevelGeneratorWindow : EditorWindow
{
    int roomCount = 5;
    int seed = 42;
    float roomSpacing = 6f;
    bool hasBossRoom = true;
    bool hasTreasureRoom = false;
    GameObject roomPrefab;

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

        if (GUILayout.Button("Generate Layout"))
        {
            GenerateLayout();
        }

        if (GUILayout.Button("Clear Layout"))
        {
            ClearLayout();
        }
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
                obj.name.Contains("boss"))
            {
                Undo.DestroyObjectImmediate(obj);
            }
        }
    }

    Color GetRoomColor(string type)
    {
        switch (type)
        {
            case "entrance":  return Color.green;
            case "boss":      return Color.red;
            case "treasure":  return Color.yellow;
            case "corridor":  return Color.grey;
            default:          return Color.white;
        }
    }
}