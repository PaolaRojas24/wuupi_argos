using System;
using TMPro;
using System.Collections;
using System.IO;
using System.Net.Sockets;
using UnityEngine;
using UnityEngine.UI;

public class CameraReceiver : MonoBehaviour
{
    public RawImage rawImage;
    private Texture2D tex;
    private TcpClient client;
    private NetworkStream stream;

    void Start()
    {
        tex = new Texture2D(2, 2);
        ConnectToPython();
    }

    void ConnectToPython()
    {
        try
        {
            client = new TcpClient("127.0.0.1", 8000);
            stream = client.GetStream();
        }
        catch
        {
            StartCoroutine(RetryConnection());
        }

    }

    IEnumerator RetryConnection()
    {
        yield return new WaitForSeconds(1f);
        ConnectToPython();
    }

    void Update()
    {
        if (stream == null || !stream.CanRead) return;

        byte[] lengthBytes = new byte[4];
        int bytesRead = stream.Read(lengthBytes, 0, 4);
        if (bytesRead == 0) return;

        int length = (lengthBytes[0] << 24) | (lengthBytes[1] << 16) | (lengthBytes[2] << 8) | lengthBytes[3];
        byte[] imageBytes = new byte[length];
        int totalRead = 0;

        while (totalRead < length)
        {
            int read = stream.Read(imageBytes, totalRead, length - totalRead);
            if (read == 0) break;
            totalRead += read;
        }

        tex.LoadImage(imageBytes); // Decodifica JPG o PNG
        rawImage.texture = tex;
    }

    void OnApplicationQuit()
    {
        stream?.Close();
        client?.Close();
    }
}
