using UnityEngine;
using System.IO;
using System.Collections.Generic;

public class LevelLoader : MonoBehaviour
{
    public GameObject roomPrefab;
    public float roomSpacing = 5f;

    [System.Serializable]
    public class Room
    {
        public string type;
        public string mood;
        public string enemies;
        public int exits;
        public string size;
        public string shape;
        public string lighting;
        public List<string> objects;
        public List<string> interactive_objects;
    }

    [System.Serializable]
    public class Connection
    {
        public int from;
        public int to;
        public string type;
    }

    [System.Serializable]
    public class LevelData
    {
        public string level_title;
        public string theme;
        public string archetype;
        public string narrative_summary;
        public List<Room> rooms;
        public List<Connection> connections;
    }

    void Start()
    {
        string path = Application.streamingAssetsPath + "/kushal_test.json";

        if (!File.Exists(path))
        {
            Debug.LogError("No layout JSON found at: " + path);
            return;
        }

        string json = File.ReadAllText(path);
        LevelData level = JsonUtility.FromJson<LevelData>(json);

        Debug.Log("Level: " + level.level_title);
        Debug.Log("Archetype: " + level.archetype);

        for (int i = 0; i < level.rooms.Count; i++)
        {
            Vector3 position = new Vector3(i * roomSpacing, 0, 0);
            GameObject room = Instantiate(roomPrefab, position, Quaternion.identity);
            room.name = level.rooms[i].type + "_" + i;
            Debug.Log("Room " + i + ": " + level.rooms[i].type +
                      " | Mood: " + level.rooms[i].mood +
                      " | Size: " + level.rooms[i].size +
                      " | Lighting: " + level.rooms[i].lighting);
        }
    }
}