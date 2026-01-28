const { Client, GatewayIntentBits, Events, ActionRowBuilder, ButtonBuilder, ButtonStyle, StringSelectMenuBuilder, EmbedBuilder, ModalBuilder, TextInputBuilder, TextInputStyle } = require('discord.js');
require('dotenv').config();

const client = new Client({ 
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildMembers
    ] 
});

// Store user responses
const userResponses = new Map();

client.once(Events.ClientReady, () => {
    console.log(`✅ Bot is online as ${client.user.tag}`);
});

// Slash command handler
client.on(Events.InteractionCreate, async interaction => {
    if (!interaction.isCommand()) return;

    const { commandName } = interaction;

    if (commandName === 'setup') {
        await showSetupMenu(interaction);
    }

    if (commandName === 'myroles') {
        await showUserRoles(interaction);
    }
});

// Button interactions
client.on(Events.InteractionCreate, async interaction => {
    if (!interaction.isButton()) return;

    const userId = interaction.user.id;
    const buttonId = interaction.customId;

    // Initialize user data if not exists
    if (!userResponses.has(userId)) {
        userResponses.set(userId, {
            favoriteSet: '',
            notifications: [],
            troopType: '',
            languages: [],
            serverRange: ''
        });
    }

    const userData = userResponses.get(userId);

    // Handle different button actions
    switch(buttonId) {
        case 'start_setup':
            await showQuestion1(interaction);
            break;
            
        case 'save_set':
            await showQuestion2(interaction);
            break;
            
        case 'save_notifications':
            await showQuestion3(interaction);
            break;
            
        case 'save_troop':
            await showQuestion4(interaction);
            break;
            
        case 'save_languages':
            await showQuestion5(interaction);
            break;
            
        case 'view_answers':
            await showAnswers(interaction);
            break;
            
        case 'edit_answers':
            await showSetupMenu(interaction);
            break;
            
        case 'close_menu':
            await interaction.deferUpdate();
            await interaction.deleteReply();
            break;
    }
});

// String select menu interactions
client.on(Events.InteractionCreate, async interaction => {
    if (!interaction.isStringSelectMenu()) return;

    const userId = interaction.user.id;
    const menuId = interaction.customId;
    const values = interaction.values;

    if (!userResponses.has(userId)) {
        userResponses.set(userId, {
            favoriteSet: '',
            notifications: [],
            troopType: '',
            languages: [],
            serverRange: ''
        });
    }

    const userData = userResponses.get(userId);

    if (menuId === 'notifications_menu') {
        userData.notifications = values;
        await interaction.reply({ 
            content: `✅ Notifications saved! You selected: ${values.map(v => `**${v}**`).join(', ')}`, 
            ephemeral: true 
        });
    }
    
    if (menuId === 'languages_menu') {
        userData.languages = values;
        await interaction.reply({ 
            content: `✅ Languages saved! You selected: ${values.map(v => `**${v}**`).join(', ')}`, 
            ephemeral: true 
        });
    }
});

// Modal submissions
client.on(Events.InteractionCreate, async interaction => {
    if (!interaction.isModalSubmit()) return;

    const userId = interaction.user.id;
    const modalId = interaction.customId;

    if (!userResponses.has(userId)) {
        userResponses.set(userId, {
            favoriteSet: '',
            notifications: [],
            troopType: '',
            languages: [],
            serverRange: ''
        });
    }

    const userData = userResponses.get(userId);

    if (modalId === 'favorite_set_modal') {
        const favoriteSet = interaction.fields.getTextInputValue('favorite_set_input');
        userData.favoriteSet = favoriteSet;
        
        await interaction.reply({ 
            content: `✅ Favorite set saved: **${favoriteSet}**\nYou will receive the **@${favoriteSet}** role.`, 
            ephemeral: true 
        });
    }
});

// Main setup menu
async function showSetupMenu(interaction) {
    const embed = new EmbedBuilder()
        .setColor(0x5865F2)
        .setTitle('🎮 Channels & Roles Setup')
        .setDescription('Customize your experience by answering a few questions to get access to more channels and roles.')
        .addFields(
            { name: '📊 Progress', value: '0/5 questions answered', inline: true },
            { name: '🕐', value: '9:23', inline: true }
        )
        .setFooter({ text: 'Click "Start Setup" to begin customizing your roles' });

    const row = new ActionRowBuilder()
        .addComponents(
            new ButtonBuilder()
                .setCustomId('start_setup')
                .setLabel('Start Setup')
                .setStyle(ButtonStyle.Primary)
                .setEmoji('⚙️'),
            new ButtonBuilder()
                .setCustomId('view_answers')
                .setLabel('View My Answers')
                .setStyle(ButtonStyle.Secondary)
                .setEmoji('📄')
        );

    await interaction.reply({ embeds: [embed], components: [row] });
}

// Question 1: Favorite Set
async function showQuestion1(interaction) {
    const modal = new ModalBuilder()
        .setCustomId('favorite_set_modal')
        .setTitle('What\'s your favorite set?');

    const favoriteSetInput = new TextInputBuilder()
        .setCustomId('favorite_set_input')
        .setLabel('Enter your favorite set name:')
        .setStyle(TextInputStyle.Short)
        .setPlaceholder('e.g., Deluxe ex')
        .setRequired(true)
        .setMaxLength(50);

    const firstActionRow = new ActionRowBuilder().addComponents(favoriteSetInput);
    modal.addComponents(firstActionRow);

    await interaction.showModal(modal);
}

// Question 2: Notifications
async function showQuestion2(interaction) {
    const embed = new EmbedBuilder()
        .setColor(0x5865F2)
        .setTitle('🔔 Question 2: Notifications')
        .setDescription('Would you like to receive ping notifications?')
        .addFields(
            { name: 'Roles you\'ll receive:', value: 'Based on your selections', inline: false }
        );

    const selectMenu = new StringSelectMenuBuilder()
        .setCustomId('notifications_menu')
        .setPlaceholder('Select notification types')
        .setMinValues(0)
        .setMaxValues(3)
        .addOptions([
            { label: 'Announcements', value: 'Announcements', emoji: '📢', description: 'Get @Announcements role' },
            { label: 'Tournaments', value: 'Tournaments', emoji: '🏆', description: 'Get @Tournaments role' },
            { label: 'Giveaways', value: 'Giveaways', emoji: '🎁', description: 'Get @Giveaways role' }
        ]);

    const row = new ActionRowBuilder()
        .addComponents(selectMenu);

    const buttonRow = new ActionRowBuilder()
        .addComponents(
            new ButtonBuilder()
                .setCustomId('save_notifications')
                .setLabel('Save & Continue')
                .setStyle(ButtonStyle.Success)
                .setEmoji('➡️')
        );

    await interaction.reply({ embeds: [embed], components: [row, buttonRow], ephemeral: true });
}

// Question 3: Troop Type
async function showQuestion3(interaction) {
    const embed = new EmbedBuilder()
        .setColor(0x5865F2)
        .setTitle('⚔️ Question 3: Troop Type')
        .setDescription('Please select your main troop type *')
        .addFields(
            { name: 'Role you\'ll receive:', value: 'Based on your selection', inline: false }
        );

    const row = new ActionRowBuilder()
        .addComponents(
            new ButtonBuilder()
                .setCustomId('troop_horde')
                .setLabel('Horde')
                .setStyle(ButtonStyle.Primary)
                .setEmoji('⚔️'),
            new ButtonBuilder()
                .setCustomId('troop_league')
                .setLabel('League')
                .setStyle(ButtonStyle.Primary)
                .setEmoji('🏅'),
            new ButtonBuilder()
                .setCustomId('troop_nature')
                .setLabel('Nature')
                .setStyle(ButtonStyle.Primary)
                .setEmoji('🌿')
        );

    const buttonRow = new ActionRowBuilder()
        .addComponents(
            new ButtonBuilder()
                .setCustomId('save_troop')
                .setLabel('Save & Continue')
                .setStyle(ButtonStyle.Success)
                .setEmoji('➡️')
        );

    await interaction.reply({ embeds: [embed], components: [row, buttonRow], ephemeral: true });
}

// Question 4: Languages
async function showQuestion4(interaction) {
    const embed = new EmbedBuilder()
        .setColor(0x5865F2)
        .setTitle('🌐 Question 4: Languages')
        .setDescription('Please select any languages you speak *')
        .addFields(
            { name: 'Roles you\'ll receive:', value: 'Based on your selections', inline: false }
        );

    const selectMenu = new StringSelectMenuBuilder()
        .setCustomId('languages_menu')
        .setPlaceholder('Select languages you speak')
        .setMinValues(0)
        .setMaxValues(4)
        .addOptions([
            { label: 'Chinese', value: 'Chinese', emoji: '🔤', description: 'Get @Chinese role' },
            { label: 'English', value: 'English', emoji: '📜', description: 'Get @English role' },
            { label: 'Japanese', value: 'Japanese', emoji: '🇯🇵', description: 'Get @Japanese role' },
            { label: 'Korean', value: 'Korean', emoji: '🇰🇷', description: 'Get @Korean role' }
        ]);

    const row = new ActionRowBuilder()
        .addComponents(selectMenu);

    const buttonRow = new ActionRowBuilder()
        .addComponents(
            new ButtonBuilder()
                .setCustomId('save_languages')
                .setLabel('Save & Continue')
                .setStyle(ButtonStyle.Success)
                .setEmoji('➡️')
        );

    await interaction.reply({ embeds: [embed], components: [row, buttonRow], ephemeral: true });
}

// Question 5: Server Range
async function showQuestion5(interaction) {
    const embed = new EmbedBuilder()
        .setColor(0x5865F2)
        .setTitle('🌍 Question 5: Server Range')
        .setDescription('Please select the server range of your main account *')
        .addFields(
            { name: 'Role you\'ll receive:', value: 'Based on your selection', inline: false }
        );

    const row = new ActionRowBuilder()
        .addComponents(
            new ButtonBuilder()
                .setCustomId('server_1')
                .setLabel('Server 1-107')
                .setStyle(ButtonStyle.Secondary),
            new ButtonBuilder()
                .setCustomId('server_2')
                .setLabel('Server 108-224')
                .setStyle(ButtonStyle.Secondary),
            new ButtonBuilder()
                .setCustomId('server_3')
                .setLabel('Server 225+')
                .setStyle(ButtonStyle.Secondary)
        );

    const buttonRow = new ActionRowBuilder()
        .addComponents(
            new ButtonBuilder()
                .setCustomId('submit_all')
                .setLabel('Submit All Answers')
                .setStyle(ButtonStyle.Success)
                .setEmoji('✅')
        );

    await interaction.reply({ embeds: [embed], components: [row, buttonRow], ephemeral: true });
}

// Show user answers
async function showAnswers(interaction) {
    const userId = interaction.user.id;
    const userData = userResponses.get(userId) || {};

    const embed = new EmbedBuilder()
        .setColor(0x5865F2)
        .setTitle('📋 Your Answers')
        .setDescription('Here are your current role preferences:')
        .addFields(
            { name: 'Favorite Set:', value: userData.favoriteSet || 'Not answered', inline: true },
            { name: 'Notifications:', value: userData.notifications?.join(', ') || 'None', inline: true },
            { name: 'Troop Type:', value: userData.troopType || 'Not answered', inline: true },
            { name: 'Languages:', value: userData.languages?.join(', ') || 'None', inline: true },
            { name: 'Server Range:', value: userData.serverRange || 'Not answered', inline: true }
        )
        .setFooter({ text: 'Use /setup to modify your answers' });

    const row = new ActionRowBuilder()
        .addComponents(
            new ButtonBuilder()
                .setCustomId('edit_answers')
                .setLabel('Edit Answers')
                .setStyle(ButtonStyle.Primary),
            new ButtonBuilder()
                .setCustomId('close_menu')
                .setLabel('Close')
                .setStyle(ButtonStyle.Secondary)
        );

    await interaction.reply({ embeds: [embed], components: [row], ephemeral: true });
}

// Login to Discord
client.login(process.env.DISCORD_TOKEN);