const { Client, GatewayIntentBits, EmbedBuilder, ActionRowBuilder, StringSelectMenuBuilder } = require('discord.js');
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
    
    const channel = client.channels.cache.get('1439070115965698099');
    if (!channel) {
        console.log('❌ Channel not found');
        return;
    }
    
    console.log(`📤 Sending to channel: ${channel.name}`);
    
    // ===== EXACT TROOP SELECTION FROM SCREENSHOT 3 =====
    const embed = new EmbedBuilder()
        .setColor(0x2f3136) // Discord dark gray
        .setTitle('Channels & Roles')
        .setDescription('```\nCustomize    All Channels\n```')
        .addFields(
            {
                name: 'Customization Questions',
                value: 'Answer questions to get access to more channels and roles.\n\u200b',
                inline: false
            },
            {
                name: 'Please select your main troop type *',
                value: '```\n- ⚔ Horde\n- 🏅 League\n- 🌿 Nature\n```\n**You will receive the @League role.**',
                inline: false
            }
        );
    
    // Dropdown menu exactly like screenshot
    const row = new ActionRowBuilder()
        .addComponents(
            new StringSelectMenuBuilder()
                .setCustomId('select_troop')
                .setPlaceholder('Select your main troop type...')
                .setMinValues(1)
                .setMaxValues(1)
                .addOptions([
                    {
                        label: 'Horde',
                        value: 'horde',
                        emoji: '⚔️',
                        description: 'Get @Horde role'
                    },
                    {
                        label: 'League', 
                        value: 'league',
                        emoji: '🏅',
                        description: 'Get @League role'
                    },
                    {
                        label: 'Nature',
                        value: 'nature',
                        emoji: '🌿',
                        description: 'Get @Nature role'
                    }
                ])
        );
    
    await channel.send({ embeds: [embed], components: [row] });
    console.log('✅ Troop selection message sent!');
});

// Optional: Handle the selection
client.on('interactionCreate', async interaction => {
    if (!interaction.isStringSelectMenu()) return;
    
    if (interaction.customId === 'select_troop') {
        const troop = interaction.values[0];
        await interaction.reply({
            content: `✅ You selected: **${troop}**\nYou will receive the **@${troop}** role.`,
            ephemeral: true
        });
    }
});

client.login(process.env.DISCORD_TOKEN).catch(error => {
    console.error('❌ Login failed:', error.message);
    process.exit(1);
});