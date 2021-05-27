The server `TaskControl` controls access to an image capturing device, for one or more clients. A client uses `TaskControl` to perform a series of image capturing tasks, each of which may take some time (think video recording, not snapshot photo). To start an image capture task, a client issues the command `Start` to the server. To stop it, the client issues command `Stop`.

While a task is in progress, i.e. after a `Start` command, the image data being obtained is temporarily stored on the server. Some time after the `Start`, the server notifies the client that started the task that there is image data available. It does so by sending the message `Ready` to the client. After this, the image data is transfered ("offloaded") to the client, and when this is done the server sends message `Completed` to the client.

This process of offloading may take a while, during which the client may already start the next task. The batches of image data that are obtained at every task are queued for offloading, and thus their associated `Ready` and `Completed` messages may lag behind the task's `Start` and `Stop` commands.

Note that it may happen that the `Ready` notification is already sent before the client says `Stop` to the server. Also the `Completed` notification may occur before the `Stop`. (This is because the server may have stopped the image capturing for some other reason than being told `Stop` by the client.)

Each task has a unique identifier, which is passed as an argument of `Start` and `Stop`. These identifiers are also passed as arguments to the `Ready` and `Completed` messages.

Assuming for the moment that there is 1 client connected to `TaskControl`, example traces are:
```
trace 1:
Start(1)
Stop(1)
Ready(1)
Completed(1)
Start(2)
Stop(2)
Ready(2)
Completed(2)
Start(3)
Stop(3)
Ready(3)
Completed(3)
Start(4)
Stop(4)
Ready(4)
Completed(4)
```
```
trace 2:
Start(1)
Ready(1)
Stop(1)
Start(4)
Completed(1)
Ready(4)
Completed(4)
Stop(4)
Start(2)
Ready(2)
Completed(2)
Stop(2)
Start(3)
Stop(3)
Ready(3)
Completed(3)
```
