import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'theme.dart';

/// Navegação inferior: Início | Pesquisar | + Preço (ação central) | Lista | Perfil.
class Shell extends StatelessWidget {
  const Shell({super.key, required this.navegacao});
  final StatefulNavigationShell navegacao;

  @override
  Widget build(BuildContext context) => Scaffold(
        body: navegacao,
        bottomNavigationBar: Container(
          decoration: const BoxDecoration(border: Border(top: BorderSide(color: Cores.borda))),
          child: NavigationBar(
            selectedIndex: navegacao.currentIndex,
            onDestinationSelected: (i) => navegacao.goBranch(i, initialLocation: i == navegacao.currentIndex),
            height: 68,
            destinations: [
              const NavigationDestination(
                  icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home_rounded), label: 'Início'),
              const NavigationDestination(icon: Icon(Icons.search_rounded), label: 'Pesquisar'),
              NavigationDestination(
                icon: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(color: Cores.verde, borderRadius: BorderRadius.circular(14)),
                  child: const Icon(Icons.add_rounded, color: Cores.branco),
                ),
                label: 'Preço',
                tooltip: 'Adicionar preço',
              ),
              const NavigationDestination(
                  icon: Icon(Icons.checklist_rounded), selectedIcon: Icon(Icons.checklist_rtl_rounded), label: 'Lista'),
              const NavigationDestination(
                  icon: Icon(Icons.person_outline_rounded), selectedIcon: Icon(Icons.person_rounded), label: 'Perfil'),
            ],
          ),
        ),
      );
}
