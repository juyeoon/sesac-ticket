import { useQuery } from "@tanstack/react-query";
import { Button, Stack } from "@mui/material";
import { systemApi } from "../../pages/system/systemApi";
import { accent, neutral } from "../../theme/tokens";

const infoButtonSx = {
    bgcolor: neutral.gray100,
    color: neutral.eerieBlack,
    cursor: "default",
    fontWeight: 700,
    whiteSpace: "nowrap",
    "&:hover": { bgcolor: accent.yellowMain },
};

/** 제출 필수조건: Front/Server version, 서버 IP를 화면에 노출. 로그인/회원가입과 같은 버튼 규격으로 보여준다. */
export function SystemInfoBadge() {
    const { data } = useQuery({
        queryKey: ["system-version"],
        queryFn: systemApi.version,
    });

    return (
        <Stack direction="row" spacing={1}>
            <Button variant="contained" disableRipple sx={infoButtonSx}>
                Front v{__APP_VERSION__}
            </Button>
            {data && (
                <>
                    <Button variant="contained" disableRipple sx={infoButtonSx}>
                        Server v{data.apiVersion}
                    </Button>
                    <Button variant="contained" disableRipple sx={infoButtonSx}>
                        X-Forwarded-For: {data.clientIp}
                    </Button>
                </>
            )}
        </Stack>
    );
}
