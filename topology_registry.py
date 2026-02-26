# Comments in English only
from __future__ import annotations
from config.paths import TABLE_DIR, TEMPLATE_FI_TEX, TEMPLATE_FE_TEX, TEMPLATE_FI_HBRIDGE_TEX
from dataclasses import dataclass
from typing import Callable, Dict, Any, Optional, Tuple

import numpy as np
import pandas as pd

from master_bank_classes import MasterBankClasses


@dataclass(frozen=True)
class TopologyConfig:
    key: str
    label: str
    compute_fn: Callable[..., Tuple[Dict[str, Any], pd.DataFrame, pd.DataFrame]]
    template_tex: str
    table_tex_filename: str
    table_xlsx_filename: str
    download_xlsx: str
    download_acp: Optional[str] = None

    def compute(self, nominal_data: Dict[str, Any]) -> Tuple[Dict[str, Any], pd.DataFrame, pd.DataFrame]:
        """Run the topology computation with the correct per-topology arguments."""
        kwargs: Dict[str, Any] = {
            "tex_filename": str(TABLE_DIR / self.table_tex_filename),
            "xlsx_filename": str(TABLE_DIR / self.table_xlsx_filename),
            "export_tex": True,
            "export_xlsx": True,
        }

        # Table 07/08 require f_values (depends on N).
        if self.key in ("yy_internal_fuses", "y_internal_fuses", "h_bridge_internal_fuses"):
            N = int(nominal_data["N"])
            kwargs["f_values"] = np.arange(N - 1).tolist()

        return self.compute_fn(nominal_data, **kwargs)


def get_topology_configs() -> Dict[str, TopologyConfig]:
    return {
        "yy_internal_fuses": TopologyConfig(
            key="yy_internal_fuses",
            label="Dupla estrela com fusíveis internos",
            compute_fn=MasterBankClasses.compute_table07_from_dict,
            template_tex=TEMPLATE_FI_TEX,
            table_tex_filename="tabela7_real.tex",
            table_xlsx_filename="tabela7_real.xlsx",
            download_xlsx="tabela7_real.xlsx",
            download_acp="TEMPLATE__FI_YY.acp",
        ),

        "y_internal_fuses": TopologyConfig(
            key="y_internal_fuses",
            label="Estrela simples com fusíveis internos",
            compute_fn=MasterBankClasses.compute_table07_single_from_dict,
            template_tex=TEMPLATE_FI_TEX,
            table_tex_filename="tabela7y_real.tex",
            table_xlsx_filename="tabela7y_real.xlsx",
            download_xlsx="tabela7y_real.xlsx",
            download_acp="TEMPLATE__FI_YY.acp",
        ),
        "h_bridge_internal_fuses": TopologyConfig(
            key="h_bridge_internal_fuses",
            label="H-Bridge com fusíveis internos",
            compute_fn=MasterBankClasses.compute_table08_from_dict,
            template_tex=TEMPLATE_FI_HBRIDGE_TEX,
            table_tex_filename="tabela8_real.tex",
            table_xlsx_filename="tabela8_real.xlsx",
            download_xlsx="tabela8_real.xlsx",
            download_acp="TEMPLATE__FI_HBridge.acp",
        ),
        "yy_external_fuses": TopologyConfig(
            key="yy_external_fuses",
            label="Dupla estrela com fusíveis externos",
            compute_fn=MasterBankClasses.compute_table03_from_dict,
            template_tex=TEMPLATE_FE_TEX,
            table_tex_filename="tabela3ext_real.tex",
            table_xlsx_filename="tabela3ext_real.xlsx",
            download_xlsx="tabela3ext_real.xlsx",
            download_acp="TEMPLATE__FE_YY.acp",
        ),
        "h_bridge_external_fuses": TopologyConfig(
            key="h_bridge_external_fuses",
            label="H-Bridge com fusíveis externos",
            compute_fn=MasterBankClasses.compute_table06_from_dict,
            template_tex=TEMPLATE_FE_TEX,
            table_tex_filename="tabela6_real.tex",
            table_xlsx_filename="tabela6_real.xlsx",
            download_xlsx="tabela6_real.xlsx",
            download_acp="TEMPLATE__FE_HBridge.acp",
        ),
    }


def get_topology_config(topology: str) -> TopologyConfig:
    configs = get_topology_configs()
    if topology not in configs:
        raise KeyError(f"Topology '{topology}' is not supported.")
    return configs[topology]
