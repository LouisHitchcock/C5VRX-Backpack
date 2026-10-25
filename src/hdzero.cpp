#include <Arduino.h>
#include "hdzero.h"
#include "msptypes.h"
#include "logging.h"
#include "time.h"

#if defined(C5VRX_USB_MIRROR)
// C5VRX bench test: echo each channel command on the backpack's USB port, since
// the real link (UART0 TX) is not visible from the host.
static const char C5VRX_BANDS[] = "ABEFRL";
static const uint16_t C5VRX_MHZ[48] = {  // ELRS order, as in rx5808.h
    5865, 5845, 5825, 5805, 5785, 5765, 5745, 5725,
    5733, 5752, 5771, 5790, 5809, 5828, 5847, 5866,
    5705, 5685, 5665, 5645, 5885, 5905, 5925, 5945,
    5740, 5760, 5780, 5800, 5820, 5840, 5860, 5880,
    5658, 5695, 5732, 5769, 5806, 5843, 5880, 5917,
    5333, 5373, 5413, 5453, 5493, 5533, 5573, 5613};
#endif

void
HDZero::Init()
{
    ModuleBase::Init();
#if defined(C5VRX_USB_MIRROR)
    USBSerial.begin();
#if defined(CONFIG_IDF_TARGET_ESP32C3)
    USBSerial.println("C5VRX backpack: HDZero MSP on UART0 TX=GPIO21 115200");
#else
    USBSerial.println("C5VRX backpack: HDZero MSP on UART0 TX=GPIO43 115200");
#endif
#endif
}

void
HDZero::SendIndexCmd(uint8_t index)
{
#if defined(C5VRX_ONE_WIRE)
    // C5VRX: TX-only link, the receiver cannot answer GET_CHANNEL_INDEX.
    // Send twice back to back; the main loop also repeats it every 2 s.
    SetChannelIndex(index);
    SetChannelIndex(index);
#if defined(C5VRX_USB_MIRROR)
    if (index < 48)
        USBSerial.printf("C5VRX backpack: SET_CHANNEL_INDEX %u = %c%u %u MHz\n", index,
                         C5VRX_BANDS[index / 8], index % 8 + 1, C5VRX_MHZ[index]);
#endif
    return;
#endif
    uint8_t retries = 3;
    while (GetChannelIndex() != index && retries > 0)
    {
        SetChannelIndex(index);
        retries--;
    }
}

uint8_t
HDZero::GetChannelIndex()
{
    MSP msp;
    mspPacket_t packet;
    packet.reset();
    packet.makeCommand();
    packet.function = MSP_ELRS_BACKPACK_GET_CHANNEL_INDEX;

    // Send request, then wait for a response back from the VRX
    bool receivedResponse = msp.awaitPacket(&packet, m_port, VRX_RESPONSE_TIMEOUT);

    if (receivedResponse)
    {
        mspPacket_t *packetResponse = msp.getReceivedPacket();
        msp.markPacketReceived();
        return packetResponse->readByte();
    }

    DBGLN("HDZero module: Exceeded timeout while waiting for channel index response");
    return CHANNEL_INDEX_UNKNOWN;
}

void
HDZero::SetChannelIndex(uint8_t index)
{
    MSP msp;
    mspPacket_t packet;
    packet.reset();
    packet.makeCommand();
    packet.function = MSP_ELRS_BACKPACK_SET_CHANNEL_INDEX;
    packet.addByte(index);  // payload

    msp.sendPacket(&packet, m_port);
#if defined(C5VRX_USB_MIRROR) && !defined(C5VRX_ONE_WIRE)
    if (index < 48)
        USBSerial.printf("C5VRX backpack: SET_CHANNEL_INDEX %u = %c%u %u MHz\n", index,
                         C5VRX_BANDS[index / 8], index % 8 + 1, C5VRX_MHZ[index]);
    else
        USBSerial.printf("C5VRX backpack: SET_CHANNEL_INDEX %u\n", index);
#endif
}

uint8_t
HDZero::GetRecordingState()
{
    MSP msp;
    mspPacket_t packet;
    packet.reset();
    packet.makeCommand();
    packet.function = MSP_ELRS_BACKPACK_GET_RECORDING_STATE;

    // Send request, then wait for a response back from the VRX
    bool receivedResponse = msp.awaitPacket(&packet, m_port, VRX_RESPONSE_TIMEOUT);

    if (receivedResponse)
    {
        mspPacket_t *packetResponse = msp.getReceivedPacket();
        msp.markPacketReceived();
        return packetResponse->readByte() ? VRX_DVR_RECORDING_ACTIVE : VRX_DVR_RECORDING_INACTIVE;
    }

    DBGLN("HDZero module: Exceeded timeout while waiting for recording state response");
    return VRX_DVR_RECORDING_UNKNOWN;
}

void
HDZero::SetRecordingState(uint8_t recordingState, uint16_t delay)
{
    DBGLN("SetRecordingState = %d delay = %d", recordingState, delay);

    MSP msp;
    mspPacket_t packet;
    packet.reset();
    packet.makeCommand();
    packet.function = MSP_ELRS_BACKPACK_SET_RECORDING_STATE;
    packet.addByte(recordingState);
    packet.addByte(delay & 0xFF); // delay byte 1
    packet.addByte(delay >> 8); // delay byte 2

    msp.sendPacket(&packet, m_port);
}

void
HDZero::SendHeadTrackingEnableCmd(bool enable)
{
    MSP msp;
    mspPacket_t packet;
    packet.reset();
    packet.makeCommand();
    packet.function = MSP_ELRS_BACKPACK_SET_HEAD_TRACKING;
    packet.addByte(enable);

    msp.sendPacket(&packet, m_port);
}

void
HDZero::SetOSD(mspPacket_t *packet)
{
    MSP msp;
    msp.sendPacket(packet, m_port);
}

void
HDZero::SetRTC()
{
    MSP msp;
    mspPacket_t packet;
    tm timeData;
    if(!getLocalTime(&timeData)) {
        DBGLN("Could not obtain time data.");
        return;
    }
    packet.reset();
    packet.makeCommand();
    packet.function = MSP_ELRS_BACKPACK_SET_RTC;
    packet.addByte(timeData.tm_year);
    packet.addByte(timeData.tm_mon);
    packet.addByte(timeData.tm_mday);
    packet.addByte(timeData.tm_hour);
    packet.addByte(timeData.tm_min);
    packet.addByte(timeData.tm_sec);

    msp.sendPacket(&packet, m_port);
}
