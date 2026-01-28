// Add this to your bot.js
client.once('ready', async () => {
    console.log('✅ Bot ready');
    
    // Find the channel by ID (your channel ID: 1439070115965698099)
    const channel = client.channels.cache.get('1439070115965698099');
    
    if (channel) {
        await channel.send({
            content: '**Please select your main troop type: ***\n\nChoose one (can be changed later):\n- ⚔️ Horde\n- 🏅 League  \n- 🌿 Nature\n\nYou will receive the @[Selected Troop] role.'
        });
        console.log('✅ Message sent to channel!');
    } else {
        console.log('❌ Channel not found. Creating one...');
        // Create a new channel
        const guild = client.guilds.cache.first();
        const newChannel = await guild.channels.create({
            name: 'select-troop',
            type: 0,
            topic: 'Choose your troop type'
        });
        await newChannel.send({
            content: '**Please select your main troop type: ***\n\nChoose one (can be changed later):\n- ⚔️ Horde\n- 🏅 League  \n- 🌿 Nature\n\nYou will receive the @[Selected Troop] role.'
        });
    }
});