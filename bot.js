const { Client, GatewayIntentBits } = require('discord.js');
require('dotenv').config();

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.GuildMembers,
        GatewayIntentBits.MessageContent
    ]
});

client.once('ready', async () => {
    console.log(`✅ Bot online as ${client.user.tag}`);
    
    // Find the channel by ID
    const channel = client.channels.cache.get('1439070115965698099');
    
    if (channel) {
        console.log(`📤 Found channel: ${channel.name}`);
        
        // Send the troop selection message
        await channel.send({
            content: '**Please select your main troop type: ***\n\nChoose one (can be changed later):\n- ⚔️ Horde\n- 🏅 League  \n- 🌿 Nature\n\nYou will receive the @[Selected Troop] role.'
        });
        
        console.log('✅ Message sent!');
    } else {
        console.log('❌ Channel not found! Listing all channels:');
        
        // List all channels to debug
        const guild = client.guilds.cache.first();
        guild.channels.cache.forEach(ch => {
            console.log(`   - ${ch.name} (${ch.id})`);
        });
        
        // Try to send to first text channel
        const firstChannel = guild.channels.cache.find(c => c.type === 0);
        if (firstChannel) {
            console.log(`📤 Sending to ${firstChannel.name} instead`);
            await firstChannel.send({
                content: '**Please select your main troop type: ***\n\nChoose one (can be changed later):\n- ⚔️ Horde\n- 🏅 League  \n- 🌿 Nature\n\nYou will receive the @[Selected Troop] role.'
            });
        }
    }
});

// Add ping command for testing
client.on('messageCreate', async message => {
    if (message.content === '!ping') {
        await message.reply('🏓 Pong! Bot is working!');
    }
    
    if (message.content === '!sendmessage') {
        const channel = client.channels.cache.get('1439070115965698099');
        if (channel) {
            await channel.send({
                content: '**Test from command!** ✅'
            });
            await message.reply('✅ Message sent!');
        }
    }
});

// Handle login errors
client.login(process.env.DISCORD_TOKEN).catch(error => {
    console.error('❌ Login failed:', error.message);
    console.log('💡 Check: 1) Token in Railway 2) Bot has permissions');
    process.exit(1);
});

// Handle crashes
process.on('unhandledRejection', error => {
    console.error('Unhandled error:', error);
});