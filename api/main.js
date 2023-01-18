let channels = new Pusher('app-key', {
    cluster: 'cluster-region',
});

let channel = channels.subscribe('channel-name');

channel.bind('event name', function(data) {

})

async function pushData(data) {
    const res = await fetch('/api/channels-event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    });
    if(!res.ok) {
        console.error('Failed to push data');
    }
}